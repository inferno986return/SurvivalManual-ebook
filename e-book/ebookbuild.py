#!/usr/bin/env python

# ebookbuild.py v1.1 - Generates a EPUB 2.0.1 file using data from metadata.json, now with lxml and orjson.

# This file is part of the ebookbuild project (also known as Project Zylon) which is licensed under GNU General Public License v3.0 (GNU GPLv3): https://www.gnu.org/licenses/gpl-3.0.en.html

import os, datetime, zipfile, hashlib, re, shutil, tempfile
import orjson
from lxml import etree
import rcssmin  # <-- Dependency for aggressive CSS minification
import htmlmin  # <-- Dependency for aggressive HTML minification

# Intro text
print(
    """
======================================================
ebookbuild 2.0.1, v1.1 - Copyright (C) 2025 Hal Motley
https://www.github.com/inferno986return/ebookbuild/
======================================================

NOTE: This program creates legacy EPUB files! Please use ebookbuild-3.3.py to create compliant EPUB 3.3 files that are recommended by the W3C.

ebookbuild is a program is designed to do one thing well. It is a Python 3 script for Windows, macOS or GNU/Linux that uses the lxml and orjson libraries to create fully-compliant EPUB 2.0.1 files that pass epubcheck and can be read with most e-readers including: Amazon Kindle, Google Play Books, Apple Books, Kobo, Nook, etc.

Not working? Try installing the dependencies:
    * lxml - 'pip install lxml'
    * orjson - 'pip install orjson'
    * rcssmin - 'pip install rcssmin'
    * htmlmin - 'pip install htmlmin'

The v1.1 release includes support for orjson and minification to make the EPUB file size smaller.

The v1.0 release includes support for infinite heading nesting in the toc.ncx, but you should use up to 4 at most. There is also support for .html files as they are supported within EPUB 2.0.1 for the sake of completion, but I don't recommend using them over .xhtml.

This program comes with ABSOLUTELY NO WARRANTY, for details see GPL-3.txt.
This is free software and you are welcome to redistribute it under certain conditions.

All trademarks belong to their respective owners.
"""
)

# JSON extraction with orjson for performance
with open("metadata.json", "rb") as json_file:
    data = orjson.loads(json_file.read())

def copy_and_log(src_dir, dst_dir):
    """
    Copies a directory tree from src_dir to dst_dir, printing each file copied.
    """
    print(f"Copying '{src_dir}' to build directory...")
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    for dirpath, _, filenames in os.walk(src_dir):
        dest_path = os.path.join(dst_dir, os.path.relpath(dirpath, src_dir))
        os.makedirs(dest_path, exist_ok=True)
        for filename in filenames:
            src_file = os.path.join(dirpath, filename)
            dst_file = os.path.join(dest_path, filename)
            clean_path = os.path.relpath(src_file, src_dir).replace('\\', '/')
            print(f"  - Copying: {clean_path}")
            shutil.copy2(src_file, dst_file)

def create_page_id(filename):
    """Generates a clean, consistent ID from a page filename."""
    page_id = filename.replace(".xhtml", "").replace(".html", "")
    page_id = re.sub(r"^\d+", "", page_id)
    page_id = re.sub(r"-", "", page_id)
    return page_id

def GenOPF(build_dir, data):
    """Generate the content.opf file inside the build directory."""
    print("Generating content.opf...")
    utctime = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    package = etree.Element("package", attrib={"xmlns": "http://www.idpf.org/2007/opf", "unique-identifier": "bookid", "version": "2.0"})
    metadata = etree.SubElement(package, "metadata", nsmap={"dc": "http://purl.org/dc/elements/1.1/", "opf": "http://www.idpf.org/2007/opf"})
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}title").text = data["title"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}creator").text = data["creator"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}subject").text = data["subject"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}publisher").text = data["publisher"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}identifier", id="bookid").text = data["ISBN"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}date").text = utctime
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}language").text = data["language"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}rights").text = data["rights"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}description").text = data["description"]
    etree.SubElement(metadata, "meta", content="cover", name="cover")
    if data.get("textPresentation") in ("Fixed layout", "Fixed Layout", "fixed layout", "fixed", "f"):
        etree.SubElement(metadata, "meta", name="fixed-layout", content="true")
    manifest = etree.SubElement(package, "manifest")
    etree.SubElement(manifest, "item", attrib={"href": "toc.ncx", "id": "ncx", "media-type": "application/x-dtbncx+xml"})
    container_path = os.path.join(build_dir, data["containerFolder"])
    cssindex = 0
    css_folder = os.path.join(container_path, data.get("cssFolder", "styles"))
    if os.path.exists(css_folder):
        for subdir, _, files in os.walk(css_folder):
            for file in files:
                if file.endswith(".css"):
                    filepath = os.path.relpath(os.path.join(subdir, file), container_path).replace("\\", "/")
                    etree.SubElement(manifest, "item", attrib={"href": filepath, "id": f"css{cssindex}", "media-type": "text/css"})
                    cssindex += 1
    imageindex = 0
    images_folder = os.path.join(container_path, data.get("imagesFolder", "images"))
    if os.path.exists(images_folder):
        for subdir, _, files in os.walk(images_folder):
            for file in files:
                filepath = os.path.relpath(os.path.join(subdir, file), container_path).replace("\\", "/")
                media_type = ""
                if file.lower().endswith((".jpg", ".jpeg", ".jpe")): media_type = "image/jpeg"
                elif file.lower().endswith(".png"): media_type = "image/png"
                elif file.lower().endswith(".gif"): media_type = "image/gif"
                if media_type:
                    item_id = "cover" if file == data["epubCover"] else f"image{imageindex}"
                    etree.SubElement(manifest, "item", attrib={"href": filepath, "id": item_id, "media-type": media_type})
                    if file != data["epubCover"]: imageindex += 1
    for page in data["pages"]:
        page_id = create_page_id(page["fileName"])
        media_type = "application/xhtml+xml" if page["fileName"].endswith((".xhtml", ".html")) else "application/octet-stream"
        etree.SubElement(manifest, "item", attrib={"href": page["fileName"], "id": page_id, "media-type": media_type})
    fontindex = 0
    fonts_folder = os.path.join(container_path, data.get("fontsFolder", "fonts"))
    if os.path.exists(fonts_folder):
        for subdir, _, files in os.walk(fonts_folder):
            for file in files:
                filepath = os.path.relpath(os.path.join(subdir, file), container_path).replace("\\", "/")
                media_type = ""
                if file.lower().endswith(".ttf"): media_type = "font/truetype"
                elif file.lower().endswith(".otf"): media_type = "font/opentype"
                if media_type:
                    etree.SubElement(manifest, "item", attrib={"href": filepath, "id": f"font{fontindex}", "media-type": media_type})
                    fontindex += 1
    spine = etree.SubElement(package, "spine", toc="ncx")
    for page in data["pages"]:
        etree.SubElement(spine, "itemref", idref=create_page_id(page["fileName"]))
    if data.get("enableGuide") in ("True", "true", "Y", "y", "yes"):
        guide = etree.SubElement(package, "guide")
        etree.SubElement(guide, "reference", type="text", href=data["startReadingfile"], title=data["startReadingpage"])
        etree.SubElement(guide, "reference", type="toc", href=data["tocFile"], title=data["tocPage"])
        etree.SubElement(guide, "reference", type="cover", href=data["frontCoverfile"], title=data["frontCoverpage"])
    tree = etree.ElementTree(package)
    output_path = os.path.join(build_dir, data["containerFolder"], "content.opf")
    tree.write(output_path, encoding="utf-8", xml_declaration=True, pretty_print=True)

def GenNCX(build_dir, data):
    """Generate the toc.ncx file inside the build directory."""
    print("Generating toc.ncx...")
    ncx = etree.Element("ncx", xmlns="http://www.daisy.org/z3986/2005/ncx/", version="2005-1")
    head = etree.SubElement(ncx, "head")
    etree.SubElement(head, "meta", name="dtb:uid", content=data["ISBN"])
    etree.SubElement(head, "meta", name="dtb:totalPageCount", content="0")
    etree.SubElement(head, "meta", name="dtb:maxPageNumber", content="0")
    doc_title = etree.SubElement(ncx, "docTitle")
    etree.SubElement(doc_title, "text").text = data["titleShort"]
    nav_map = etree.SubElement(ncx, "navMap")
    play_order_counter, max_depth = 1, 0
    def add_nav_point(parent, item, current_depth):
        nonlocal play_order_counter, max_depth
        nav_point = etree.SubElement(parent, "navPoint", id=f"navpoint-{play_order_counter}", playOrder=str(play_order_counter))
        nav_label = etree.SubElement(nav_point, "navLabel")
        etree.SubElement(nav_label, "text").text = item["pageName"]
        etree.SubElement(nav_point, "content", src=item["fileName"])
        play_order_counter += 1
        max_depth = max(max_depth, current_depth)
        if "subheadings" in item and item["subheadings"]:
            for subitem in item["subheadings"]:
                add_nav_point(nav_point, subitem, current_depth + 1)
    for page in data["pages"]:
        add_nav_point(nav_map, page, 1)
    etree.SubElement(head, "meta", name="dtb:depth", content=str(max_depth))
    tree = etree.ElementTree(ncx)
    output_path = os.path.join(build_dir, data["containerFolder"], "toc.ncx")
    tree.write(output_path, encoding="utf-8", xml_declaration=True, pretty_print=True)

def GenMetadata(build_dir, data):
    """Create the mimetype and container.xml files inside the build directory."""
    print("Generating container metadata...")
    with open(os.path.join(build_dir, "mimetype"), "w") as mime:
        mime.write("application/epub+zip")
    meta_inf_dir = os.path.join(build_dir, "META-INF")
    os.makedirs(meta_inf_dir, exist_ok=True)
    container = etree.Element("container", version="1.0", xmlns="urn:oasis:names:tc:opendocument:xmlns:container")
    rootfiles = etree.SubElement(container, "rootfiles")
    etree.SubElement(rootfiles, "rootfile", attrib={"full-path": data["containerFolder"] + "/content.opf", "media-type": "application/oebps-package+xml"})
    tree = etree.ElementTree(container)
    tree.write(os.path.join(meta_inf_dir, "container.xml"), encoding="utf-8", xml_declaration=True, pretty_print=True)

def GenMinify(build_dir, data):
    """Aggressively minifies XHTML and CSS files using focused libraries."""
    print("\nChecking minification settings...")
    TRUTHY_VALUES = ("True", "true", "Yes", "yes", "Y", "y")
    
    # This logic is now robust and checks for old and new keys in metadata.json
    should_minify_html = (data.get("minifyXHTML") in TRUTHY_VALUES) or \
                         (data.get("minifyXHTMLcomments") in TRUTHY_VALUES) or \
                         (data.get("minifyXHTMLwhitespace") in TRUTHY_VALUES)

    should_minify_css = (data.get("minifyCSS") in TRUTHY_VALUES) or \
                        (data.get("minifyCSScomments") in TRUTHY_VALUES) or \
                        (data.get("minifyCSSwhitespace") in TRUTHY_VALUES)

    should_add_copyright = (data.get("minifyCopyright") in TRUTHY_VALUES) or \
                           (data.get("minifyXHTMLcopyright") in TRUTHY_VALUES) or \
                           (data.get("minifyCSScopyright") in TRUTHY_VALUES)
    
    copyright_notice = data.get("copyrightNotice", "")

    if not (should_minify_html or should_minify_css):
        print("No minification options enabled. Skipping.")
        return

    print("Starting aggressive minification process...")
    container_path = os.path.join(build_dir, data["containerFolder"])
    
    for subdir, _, files in os.walk(container_path):
        for file in files:
            full_path = os.path.join(subdir, file)
            
            # --- CSS Minification ---
            if file.lower().endswith(".css") and should_minify_css:
                print(f"  - Minifying CSS: {os.path.basename(file)}")
                with open(full_path, "r", encoding="utf-8") as f:
                    css_content = f.read()
                
                minified_css = rcssmin.cssmin(css_content)
                
                if should_add_copyright and copyright_notice:
                    minified_css = f"/*{copyright_notice}*/" + minified_css
                
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(minified_css)

            # --- HTML Minification ---
            elif file.lower().endswith((".xhtml", ".html")) and should_minify_html:
                print(f"  - Minifying HTML: {os.path.basename(file)}")
                with open(full_path, "r", encoding="utf-8") as f:
                    html_content = f.read()

                minified_html = htmlmin.minify(html_content, remove_comments=True, remove_empty_space=True)
                
                if should_add_copyright and copyright_notice:
                    minified_html = f"" + minified_html

                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(minified_html)

    print("Minification complete.")

def GenEpub(build_dir, data):
    """Generate the EPUB file from the contents of the build directory."""
    print("\nPackaging EPUB file...")
    epub_filename = data["fileName"] + ".epub"
    mimetype_path = os.path.join(build_dir, "mimetype")
    with zipfile.ZipFile(epub_filename, mode="w", compression=zipfile.ZIP_STORED) as zf:
        zf.write(mimetype_path, arcname="mimetype")
    with zipfile.ZipFile(epub_filename, mode="a", compression=zipfile.ZIP_DEFLATED) as zf:
        for dirname, _, files in os.walk(build_dir):
            for filename in files:
                if filename == "mimetype": continue
                full_path = os.path.join(dirname, filename)
                arcname = os.path.relpath(full_path, build_dir).replace("\\", "/")
                print(f"  - Zipping: {arcname}")
                zf.write(full_path, arcname)
    with open(epub_filename, "rb") as f:
        if zipfile.is_zipfile(f): print(f"\nEPUB file '{epub_filename}' created successfully.")
        else: print(f"\nError: '{epub_filename}' is not a valid ZIP file.")

def GenChksum():
    """Generate and display checksums for the final EPUB file."""
    print("\nChecking checksum generation settings...")
    if data.get("enableChecksums") not in ("True", "true", "Yes", "yes", "Y", "y"):
        print("Checksum generation disabled. Skipping.")
        return
    print("Generating checksums...")
    epub_filename = data["fileName"] + ".epub"
    utctime = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(" ")
    md5, sha256, sha512 = hashlib.md5(), hashlib.sha256(), hashlib.sha512()
    with open(epub_filename, "rb") as afile:
        buffer = afile.read()
        md5.update(buffer)
        sha256.update(buffer)
        sha512.update(buffer)
    checksum_output = f"""
-This output is saved to checksums.txt-
WARNING: MD5 is cryptographically weak and is not recommended for verifying file integrity! Use SHA-256 or SHA-512 instead.
Checksum values for {epub_filename} on {str(utctime)} UTC
==========================================================
MD5: {md5.hexdigest()}
SHA-256: {sha256.hexdigest()}
SHA-512: {sha512.hexdigest()}
"""
    print(checksum_output)
    with open("checksums.txt", "w") as chksum:
        chksum.write(f"Checksum values for {epub_filename} on {str(utctime)} UTC\n\n")
        chksum.write("WARNING: MD5 is cryptographically weak and is not recommended for verifying file integrity! Use SHA-256 or SHA-512 instead.\n\n")
        chksum.write("=================================================================================\n\n")
        chksum.write(f"MD5: {md5.hexdigest()}\n")
        chksum.write(f"SHA-256: {sha256.hexdigest()}\n")
        chksum.write(f"SHA-512: {sha512.hexdigest()}\n")

# Main execution block
if __name__ == "__main__":
    build_dir = tempfile.mkdtemp()
    print(f"Created temporary build directory: {build_dir}")
    try:
        # 1. Copy source content to the build directory
        source_oebps = data["containerFolder"]
        copy_and_log(source_oebps, os.path.join(build_dir, source_oebps))

        # 2. Generate metadata files directly into the build directory
        GenMetadata(build_dir, data)
        GenOPF(build_dir, data)
        GenNCX(build_dir, data)

        # 3. Run minification on the copied files
        GenMinify(build_dir, data)

        # 4. Package the contents of the build directory into the .epub file
        GenEpub(build_dir, data)
        
        # 5. Generate checksum for the final .epub file
        GenChksum()
        
        print("\nAll tasks completed successfully!")
    
    except FileNotFoundError as e:
        print("\n" + "="*60)
        print(">>> A FILE NOT FOUND ERROR OCCURRED! SCRIPT HALTED. <<<")
        print("This usually means a file or folder specified in 'metadata.json' does not exist.")
        print(f"DETAILS: {e}")
        print("="*60 + "\n")

    except Exception as e:
        print("\n" + "="*60)
        print(">>> AN UNEXPECTED ERROR OCCURRED! SCRIPT HALTED. <<<")
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"DETAILS: {e}")
        print("="*60 + "\n")
        
    finally:
        # 6. Cleanup by deleting the temporary build directory
        print(f"Cleaning up build directory: {build_dir}")
        shutil.rmtree(build_dir)