# Conversion Notes
* Initial conversion of MarkDown files to HTML via pandoc using this Bash command (courtesy of: https://www.dyrobooks.com/blog/2018/06/30/batch-convert-files-with-pandoc/ ): `for i in *.md ; do echo "$i" && pandoc -s $i -o $i.html ; done`
* Added icons to the Contents. I exported them from the Material site as rounded white icons in the .svg format that are 18dp in size. Looks good with the icon at 11px (tall) and exported to 40px (squared) in total size.
* Added coloured boxes for warning and caution text throughout the book.
* In Power, I have used an ordered list at the top for the two items and unordered lists to replace the codeboxes (unneccessary here).
* Corrected "Psycology" typo in the Apps chapter.
* In Medicine, the figure 4-1 image is not available on the wiki, but is on the app. What's going on there?
* In Water, corrected "dehydrate" typo in the fluids table (I also need to get a proper table CSS class going there)
* In Food, added an ordered list for several lists that were marked with an asterisk including the fish poisoning list.
* In Food, why is each paragraph numbered? Have the paragraphs just been copied verbatim from the original US Army FM guide?
* In Desert, there are also paragraph numbers like with the Food chapter.