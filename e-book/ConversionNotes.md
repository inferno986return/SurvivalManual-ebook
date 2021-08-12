# Conversion Notes
* Initial conversion of MarkDown files to HTML via pandoc using this Bash command (courtesy of: https://www.dyrobooks.com/blog/2018/06/30/batch-convert-files-with-pandoc/ ): `for i in *.md ; do echo "$i" && pandoc -s $i -o $i.html ; done`
* Added icons to the Contents. I exported them from the Material site as rounded white icons in the .svg format that are 18dp in size. Looks good with the icon at 11px (squared) and exported to 40px (squared) in total size.
* In Power, I have used an ordered list at the top for the two items and unordered lists to replace the codeboxes (unneccessary here).
* Corrected "Psycology" typo in the Apps chapter