# ebookbuild-oop-3.3.py - Create EPUB 3.3-compliant files

import os, datetime, json, zipfile, hashlib, re
from collections import OrderedDict

# intro text
print("""
================================================
ebookbuild, v1.0 - Copyright (C) 2023 Hal Motley
https://www.github.com/inferno986return/ebookbuild/
================================================

This program comes with ABSOLUTELY NO WARRANTY, for details see GPL-3.txt.
This is free software and you are welcome to redistribute it under certain conditions.

""")

class GenOPF: # GenOPF - generate the .opf file, such as: content.opf, package.opf, etc.
    def __init__(self, file_name):
        self.file_name = file_name
class GenNCX: # GenNCX - generate a toc.ncx to provide legacy support for older e-readers

class GenEPUB: # GenEPUB - add the files and folders recursively, also check the META-INF, mimetype and container.xml files are present


class GenChecksum: # GenChecksum = generate the checksums
    def __init__(self, file_name, output_file="checksums.txt"):
        self.file_name = file_name # "checksums.txt"
        self.md5 = hashlib.md5()
        self.sha256 = hashlib.sha256()
        self.sha512 = hashlib.sha512()

    def generate_checksums(self):
        utctime = datetime.datetime.utcnow().replace(microsecond=0).isoformat(' ')

        with open(self.file_name + ".epub", 'rb') as afile:
            buffer = afile.read()

            self.md5.update(buffer)
            self.sha256.update(buffer)
            self.sha512.update(buffer)

            # Seperates the checksum output from the files going into the book.
            print("\n- Output saved to checksums.txt -\n")
            print(f"Checksum values for {self.file_name}.epub on {utctime} UTC")
            print("=" * 75)
            print(f"MD5: {self.md5.hexdigest()}")
            print(f"SHA-256: {self.sha256.hexdigest()}")
            print(f"SHA-512: {self.sha512.hexdigest()}\n")

            with open("checksums.txt", "w") as chksum:
                chksum.write("Checksum values for " + self.file_name + ".epub on " + str(utctime) + "UTC" + "\n")
                chksum.write("=================================================================================\n")
                chksum.write("\n")
                chksum.write("MD5: " + self.md5.hexdigest() + "\n")
                chksum.write("SHA-256: " + self.sha256.hexdigest() + "\n")
                chksum.write("SHA-512: " + self.sha512.hexdigest() + "\n")

# Usage
data = {"fileName": "your_filename"}
checksum_generator = GenChecksum(data["fileName"])
checksum_generator.generate_checksums()