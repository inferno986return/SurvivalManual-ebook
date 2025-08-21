#!/usr/bin/env python

# ebookbuild.py v1.3 - Generates an EPUB 3.3 file using data from metadata.json, now with lxml and orjson.

# This file is part of the ebookbuild project (also known as Project Zylon) which is licensed under GNU General Public License v3.0 (GNU GPLv3): https://www.gnu.org/licenses/gpl-3.0.en.html

import os, datetime, zipfile, hashlib
import orjson
from lxml import etree

# Intro text
print(
    """
======================================================
ebookbuild 3.3, v1.5 - Copyright (C) 2025 Hal Motley
https://www.github.com/inferno986return/ebookbuild/
======================================================

NOTE: This program creates EPUB 3.3 files that are recommended by the W3C!

This script uses the lxml and orjson libraries to create fully-compliant
EPUB 3.3 files that pass epubcheck and can be read with most e-readers.

Not working? Try installing the dependencies:
    * lxml - 'pip install lxml'
    * orjson - 'pip install orjson'

This program comes with ABSOLUTELY NO WARRANTY; for details see the license.
This is free software, and you are welcome to redistribute it
under certain conditions. All trademarks belong to their respective owners.
"""
)

# JSON extraction with orjson for performance
try:
    with open("metadata.json", "rb") as json_file:
        data = orjson.loads(json_file.read())
except FileNotFoundError:
    print("FATAL ERROR: metadata.json not found. The script cannot continue.")
    exit()

def create_page_id(filename):
    """Generates a clean, consistent ID from a page filename."""
    # This simplified version creates unique IDs like "0100", "0200", etc.
    page_id = filename.split('#')[0].replace(".xhtml", "").replace(".html", "")
    page_id = page_id.replace("-", "")
    return page_id

def GenOPF(output_dir, data):
    """Generate the content.opf file for EPUB 3.3."""
    print("Generating content.opf...")
    utctime = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    nsmap = {"dc": "http://purl.org/dc/elements/1.1/", None: "http://www.idpf.org/2007/opf"}
    package = etree.Element("package", attrib={"unique-identifier": "bookid", "version": "3.0"}, nsmap=nsmap)
    
    # --- METADATA (No changes needed) ---
    metadata = etree.SubElement(package, "metadata")
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}identifier", id="bookid").text = data["ISBN"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}title").text = data["title"]
    
    i = 1
    while True:
        creator_key = f"creator{i}"
        role_key = f"creator{i}Role"
        if creator_key in data:
            creator_id = f"creator{i}"
            etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}creator", id=creator_id).text = data[creator_key]
            if role_key in data:
                etree.SubElement(metadata, "meta", refines=f"#{creator_id}", property="role", scheme="marc:relators").text = data[role_key]
            i += 1
        else:
            break

    i = 1
    while True:
        contrib_key = f"contributor{i}"
        role_key = f"contributor{i}Role"
        if contrib_key in data:
            contrib_id = f"contributor{i}"
            etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}contributor", id=contrib_id).text = data[contrib_key]
            if role_key in data:
                etree.SubElement(metadata, "meta", refines=f"#{contrib_id}", property="role", scheme="marc:relators").text = data[role_key]
            i += 1
        else:
            break
            
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}publisher").text = data["publisher"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}language").text = data["language"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}rights").text = data["rights"]
    if data.get("date"):
        etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}date").text = data["date"]
    
    if data.get("sourceUrn") and data.get("sourceISBN"):
        urn_type = data["sourceUrn"].lower()
        source_id = data["sourceISBN"]
        source_urn = f"urn:{urn_type}:{source_id}"
        etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}source").text = source_urn
    
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}description").text = data["description"]
    etree.SubElement(metadata, "meta", property="dcterms:modified").text = utctime
    
    if ("collection" in data and
        data["collection"].get("enableCollection") == "true" and
        all(k in data["collection"] for k in ["name", "type", "position"])):
        collection_data = data["collection"]
        etree.SubElement(metadata, "meta", property="belongs-to-collection", id="collection").text = collection_data["name"]
        etree.SubElement(metadata, "meta", refines="#collection", property="collection-type").text = collection_data["type"]
        etree.SubElement(metadata, "meta", refines="#collection", property="group-position").text = str(collection_data["position"])
        if collection_data.get("fileAs"):
            etree.SubElement(metadata, "meta", refines="#collection", property="file-as").text = collection_data["fileAs"]
        if collection_data.get("alternativeScript"):
            etree.SubElement(metadata, "meta", refines="#collection", property="alternate-script").text = collection_data["alternativeScript"]

    etree.SubElement(metadata, "meta", name="cover", content="cover-image")

    # --- MANIFEST & SPINE GENERATION ---
    manifest = etree.SubElement(package, "manifest")
    spine_attrs = {}
    if data.get("enableNcx") == "true":
        spine_attrs['toc'] = 'ncx'
    spine = etree.SubElement(package, "spine", **spine_attrs)

    # Add navigation documents
    etree.SubElement(manifest, "item", id="nav", href=data["navDocFile"], **{"media-type": "application/xhtml+xml", "properties": "nav"})
    if data.get("enableNcx") == "true":
        etree.SubElement(manifest, "item", id="ncx", href="toc.ncx", **{"media-type": "application/x-dtbncx+xml"})
    
    # OPTIMIZED: Process pages for manifest and spine in a single pass
    xhtml_idx = 0
    seen_filenames = set()
    for page in data["pages"]:
        base_filename = page["fileName"].split('#')[0]
        if base_filename not in seen_filenames:
            page_id = f"xhtml{xhtml_idx}"
            
            # Add to manifest
            etree.SubElement(manifest, "item", id=page_id, href=base_filename, **{"media-type": "application/xhtml+xml"})
            
            # Add to spine
            itemref = etree.SubElement(spine, "itemref", idref=page_id)
            if page.get("type") == "cover":
                itemref.set("linear", "no")
            
            seen_filenames.add(base_filename)
            xhtml_idx += 1

    # Process asset files (CSS, images, fonts) with per-type counters
    asset_counters = {}
    for folder_key, ext_map in [
        ("cssFolder", {".css": "text/css"}),
        ("imagesFolder", {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif"}),
        ("fontsFolder", {".ttf": "font/truetype", ".otf": "font/opentype", ".woff": "font/woff", ".woff2": "font/woff2"})
    ]:
        folder_name = data.get(folder_key)
        if folder_name:
            folder_path = os.path.join(output_dir, folder_name)
            if os.path.exists(folder_path):
                for file in sorted(os.listdir(folder_path)):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in ext_map:
                        if file == data["epubCover"]:
                            item_id = "cover-image"
                        else:
                            prefix = ext.strip('.')
                            idx = asset_counters.get(prefix, 0)
                            item_id = f"{prefix}{idx}"
                            asset_counters[prefix] = idx + 1
                        
                        attrs = {"id": item_id, "href": f"{folder_name}/{file}", "media-type": ext_map[ext]}
                        if file == data["epubCover"]:
                            attrs["properties"] = "cover-image"
                        etree.SubElement(manifest, "item", **attrs)

    tree = etree.ElementTree(package)
    output_path = os.path.join(output_dir, "content.opf")
    tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)

def GenNav(output_dir, data):
    """Generate the nav.xhtml file required by EPUB 3."""
    print("Generating nav.xhtml...")
    
    def build_nav_list(parent_ol, items):
        for item in items:
            li = etree.SubElement(parent_ol, "li")
            etree.SubElement(li, "a", href=item["fileName"]).text = item["pageName"]
            if "subheadings" in item and item["subheadings"]:
                nested_ol = etree.SubElement(li, "ol")
                build_nav_list(nested_ol, item["subheadings"])

    nav_html = etree.Element("html", nsmap={None: "http://www.w3.org/1999/xhtml", "epub": "http://www.idpf.org/2007/ops"})
    head = etree.SubElement(nav_html, "head")
    etree.SubElement(head, "title").text = data["tocTitle"]
    body = etree.SubElement(nav_html, "body")
    
    # This part generates the main Table of Contents
    nav = etree.SubElement(body, "nav", **{"{http://www.idpf.org/2007/ops}type": "toc", "id": "toc"})
    etree.SubElement(nav, "h1").text = data["tocTitle"]
    ol = etree.SubElement(nav, "ol")
    build_nav_list(ol, data["pages"])

    # Add the landmarks navigation structure, replacing the old <guide>
    if data.get("enableGuide") == "true":
        # Create the <nav> element with epub:type="landmarks"
        landmarks_nav = etree.SubElement(body, "nav", **{"{http://www.idpf.org/2007/ops}type": "landmarks", "id": "landmarks"})
        etree.SubElement(landmarks_nav, "h1").text = "Landmarks"
        landmarks_ol = etree.SubElement(landmarks_nav, "ol")
        
        # Add landmark for the cover page
        cover_li = etree.SubElement(landmarks_ol, "li")
        etree.SubElement(cover_li, "a", **{
            "{http://www.idpf.org/2007/ops}type": "cover", 
            "href": data["frontCoverfile"]
        }).text = data["frontCoverpage"]
        
        # Add landmark for the Table of Contents page
        toc_li = etree.SubElement(landmarks_ol, "li")
        etree.SubElement(toc_li, "a", **{
            "{http://www.idpf.org/2007/ops}type": "toc", 
            "href": data["tocFile"]
        }).text = data["tocPage"]
        
        # Add landmark for the "start reading" page (bodymatter)
        start_li = etree.SubElement(landmarks_ol, "li")
        etree.SubElement(start_li, "a", **{
            "{http://www.idpf.org/2007/ops}type": "bodymatter", 
            "href": data["startReadingfile"]
        }).text = data["startReadingpage"]

    tree = etree.ElementTree(nav_html)
    output_path = os.path.join(output_dir, data["navDocFile"])
    tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True, doctype='<!DOCTYPE html>')
    
def GenNCX(output_dir, data):
    """Generate the toc.ncx file for backward compatibility."""
    if data.get("enableNcx") != "true":
        print("Skipping toc.ncx generation as 'enableNcx' is not 'true'.")
        return
        
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
    output_path = os.path.join(output_dir, "toc.ncx")
    tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)

def GenPackagingFiles(data):
    """Check, inspect, and create the mimetype and container.xml files if needed."""
    print("Checking container metadata...")
    
    # --- 1. Handle mimetype file ---
    mimetype_content = "application/epub+zip"
    write_mimetype = True
    if os.path.exists("mimetype"):
        with open("mimetype", "r") as f:
            if f.read() == mimetype_content:
                print("  - mimetype file is already correct. Leaving it alone.")
                write_mimetype = False
            else:
                print("  - WARNING: mimetype file is incorrect. Overwriting.")
    if write_mimetype:
        print("  - Creating mimetype file.")
        with open("mimetype", "w") as mime:
            mime.write(mimetype_content)

    # --- 2. Handle container.xml file ---
    meta_inf_dir = "META-INF"
    container_path = os.path.join(meta_inf_dir, "container.xml")
    os.makedirs(meta_inf_dir, exist_ok=True)
    
    expected_path = f"{data['containerFolder']}/content.opf"
    write_container = True
    if os.path.exists(container_path):
        try:
            tree = etree.parse(container_path)
            ns = {'c': 'urn:oasis:names:tc:opendocument:xmlns:container'}
            rootfile = tree.find('c:rootfiles/c:rootfile', namespaces=ns)
            if rootfile is not None and rootfile.get('full-path') == expected_path:
                print("  - container.xml is already correct. Leaving it alone.")
                write_container = False
            else:
                print("  - WARNING: container.xml has incorrect path. Overwriting.")
        except etree.XMLSyntaxError:
            print("  - WARNING: container.xml is malformed. Overwriting.")
            
    if write_container:
        print("  - Creating container.xml.")
        container = etree.Element("container", version="1.0", xmlns="urn:oasis:names:tc:opendocument:xmlns:container")
        rootfiles = etree.SubElement(container, "rootfiles")
        etree.SubElement(rootfiles, "rootfile", **{"full-path": expected_path, "media-type": "application/oebps-package+xml"})
        tree = etree.ElementTree(container)
        tree.write(container_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)

def GenEpub(data):
    """Generate the EPUB file from the project contents."""
    print("\nPackaging EPUB file...")
    epub_filename = data["fileName"] + ".epub"
    
    with zipfile.ZipFile(epub_filename, mode="w", compression=zipfile.ZIP_STORED) as zf:
        zf.write("mimetype", arcname="mimetype")
        
    with zipfile.ZipFile(epub_filename, mode="a", compression=zipfile.ZIP_DEFLATED) as zf:
        if os.path.isdir("META-INF"):
            zf.write("META-INF/container.xml", arcname="META-INF/container.xml")
        
        source_dir = data["containerFolder"]
        for dirname, _, files in os.walk(source_dir):
            for filename in files:
                full_path = os.path.join(dirname, filename)
                arcname = full_path.replace("\\", "/")
                print(f"  - Zipping: {arcname}")
                zf.write(full_path, arcname)
                
    if zipfile.is_zipfile(epub_filename):
        print(f"\nEPUB file '{epub_filename}' created successfully.")
    else:
        print(f"\nError: '{epub_filename}' is not a valid ZIP file.")

def GenChksum(data):
    """Generate checksums for the final EPUB file."""
    if data.get("enableChecksums") != "true":
        print("\nChecksum generation disabled. Skipping.")
        return
        
    print("\nGenerating checksums...")
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
WARNING: MD5 is cryptographically weak. Use SHA-256 or SHA-512 instead.
Checksum values for {epub_filename} on {str(utctime)} UTC
==========================================================
MD5: {md5.hexdigest()}
SHA-256: {sha256.hexdigest()}
SHA-512: {sha512.hexdigest()}
"""
    print(checksum_output)
    with open("checksums.txt", "w") as chksum:
        chksum.write(checksum_output.strip())

def GenMetainf(data):
    """Runs the main build process for the e-book."""
    try:
        oebps_dir = data["containerFolder"]
        if not os.path.isdir(oebps_dir):
             raise FileNotFoundError(f"The container folder '{oebps_dir}' does not exist.")

        # 1. Check/create packaging metadata (mimetype, container.xml)
        GenPackagingFiles(data)

        # 2. Generate/overwrite files directly in the OEBPS folder
        GenOPF(oebps_dir, data)
        GenNav(oebps_dir, data)
        GenNCX(oebps_dir, data)

        # 3. Package the contents into the .epub file
        GenEpub(data)
        
        # 4. Generate checksum for the final .epub file
        GenChksum(data)
        
        print("\nAll tasks completed successfully!")
    
    except FileNotFoundError as e:
        print("\n" + "="*60)
        print(">>> A FILE NOT FOUND ERROR OCCURRED! SCRIPT HALTED. <<<")
        print(f"DETAILS: {e}")
        print("="*60 + "\n")
    except Exception as e:
        print("\n" + "="*60)
        print(">>> AN UNEXPECTED ERROR OCCURRED! SCRIPT HALTED. <<<")
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"DETAILS: {e}")
        print("="*60 + "\n")
        
# Main execution block
if __name__ == "__main__":
    GenMetainf(data)