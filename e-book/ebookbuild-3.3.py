#!/usr/bin/env python

# ebookbuild.py v1.4.2 - Generates an EPUB 3.3 file using data from metadata.json, now with lxml and orjson.

# This file is part of the ebookbuild project (also known as Project Zylon) which is licensed under GNU General Public License v3.0 (GNU GPLv3): https://www.gnu.org/licenses/gpl-3.0.en.html

import os, datetime, zipfile, hashlib
import orjson
from lxml import etree

# Intro text
print(
    """
======================================================
ebookbuild 3.3, v1.4.3 - Copyright (C) 2025 Hal Motley
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

    nsmap = {
        "dc": "http://purl.org/dc/elements/1.1/",
        None: "http://www.idpf.org/2007/opf"
    }

    package = etree.Element("package", attrib={"unique-identifier": "bookid", "version": "3.0"}, nsmap=nsmap)
    metadata = etree.SubElement(package, "metadata")

    # --- METADATA ---
    # Identifier with refinement for ISBN
    identifier_el = etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}identifier", id="bookid")
    identifier_el.text = data["ISBN"]
    etree.SubElement(metadata, "meta", refines="#bookid", property="identifier-type", scheme="xsd:string").text = "ISBN"

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


    # --- THE ELEGANT ARCHITECTURE: MANIFEST & SPINE ---

    # 1. Asset Definitions
    SUPPORTED_ASSETS = {
        ".xhtml": "application/xhtml+xml", ".html": "application/xhtml+xml",
        ".css": "text/css", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp", ".ttf": "font/truetype",
        ".otf": "font/opentype", ".woff": "font/woff", ".woff2": "font/woff2", ".mp3": "audio/mpeg",
        ".mp4": "video/mp4", ".m4a": "audio/mp4", ".m4v": "video/mp4", ".opus": "audio/opus",
        ".pls": "application/pls+xml", ".smil": "application/smil+xml"
    }

    # 2. Build the File Registry (Single Source of Truth)
    manifest_registry = {}  # Maps filepath -> unique_id
    asset_counters = {}
    
    # Pre-register reserved IDs mapping to your metadata
    manifest_registry[data["navDocFile"]] = "nav"
    if data.get("enableNcx") == "true":
        manifest_registry["toc.ncx"] = "ncx"

    # Extract the cover filename to search for it during the walk
    epub_cover_filename = data.get("epubCover")

    # Walk the directory ONCE to index all actual files
    for dirpath, _, filenames in os.walk(output_dir):
        for file in sorted(filenames):
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_ASSETS:
                href_path = os.path.relpath(os.path.join(dirpath, file), output_dir).replace(os.sep, '/')
                
                if href_path not in manifest_registry:
                    # Automatically find the cover image regardless of what subfolder it is in
                    if epub_cover_filename and file == epub_cover_filename:
                        manifest_registry[href_path] = "cover-image"
                    else:
                        # Assign dynamic IDs for everything else
                        prefix = ext.strip('.')
                        idx = asset_counters.get(prefix, 0)
                        manifest_registry[href_path] = f"{prefix}{idx}"
                        asset_counters[prefix] = idx + 1

    # 3. Generate Manifest using the Registry
    manifest = etree.SubElement(package, "manifest")
    for href, item_id in manifest_registry.items():
        ext = os.path.splitext(href)[1].lower()
        
        # Determine media-type (handling ncx override)
        media_type = "application/x-dtbncx+xml" if item_id == "ncx" else SUPPORTED_ASSETS.get(ext, "application/xhtml+xml")
        
        attrs = {"id": item_id, "href": href, "media-type": media_type}
        
        if item_id == "nav":
            attrs["properties"] = "nav"
        elif item_id == "cover-image":
            attrs["properties"] = "cover-image"
            
        etree.SubElement(manifest, "item", **attrs)

    # 4. Generate Spine by querying the Registry
    spine_attrs = {}
    if data.get("enableNcx") == "true":
        spine_attrs['toc'] = 'ncx'
        
    spine = etree.SubElement(package, "spine", **spine_attrs)

    seen_spine_items = set()

    def process_spine_items(items):
        for item in items:
            base_filename = item["fileName"].split('#')[0]
            
            if base_filename not in seen_spine_items:
                item_id = manifest_registry.get(base_filename)
                if item_id:
                    itemref = etree.SubElement(spine, "itemref", idref=item_id)
                    if item.get("type") == "cover":
                        itemref.set("linear", "no")
                else:
                    print(f"  -> WARNING: Spine item '{base_filename}' missing from output folder. Excluded from OPF.")
                
                seen_spine_items.add(base_filename)
            
            # Recursively process nested subheadings so they get added to the spine
            if "subheadings" in item and item["subheadings"]:
                process_spine_items(item["subheadings"])

    # Trigger the function starting with the main pages array
    process_spine_items(data["pages"])

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
        
    checksum_output = f"""-This output is saved to checksums.txt-

WARNING: MD5 is cryptographically weak. Use SHA-256 or SHA-512 instead.

Checksum values for {epub_filename} on {str(utctime)} UTC
=======================================================================

MD5: {md5.hexdigest()}
SHA-256: {sha256.hexdigest()}
SHA-512: {sha512.hexdigest()}
"""
    print(checksum_output)
    with open("checksums.txt", "w") as chksum:
        chksum.write(checksum_output)

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
        print("\n" + "="*70)
        print(">>> A FILE NOT FOUND ERROR OCCURRED! SCRIPT HALTED. <<<")
        print(f"DETAILS: {e}")
        print("="*70 + "\n")
    except Exception as e:
        print("\n" + "="*70)
        print(">>> AN UNEXPECTED ERROR OCCURRED! SCRIPT HALTED. <<<")
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"DETAILS: {e}")
        print("="*70 + "\n")
        
# Main execution block
if __name__ == "__main__":
    GenMetainf(data)