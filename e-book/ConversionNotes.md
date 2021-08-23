# Conversion Notes
* Initial conversion of MarkDown files to HTML via pandoc using this Bash command (courtesy of: https://www.dyrobooks.com/blog/2018/06/30/batch-convert-files-with-pandoc/ ): `for i in *.md ; do echo "$i" && pandoc -s $i -o $i.html ; done`
* Added icons to the Contents. I exported them from the Material site as rounded white icons in the .svg format that are 18dp in size. Looks good with the icon at 11px (tall) and exported to 40px (squared) in total size.
* Added coloured boxes for warning and caution text throughout the book.
* All the headings will need to be made consistent.
* In Power, I have used an ordered list at the top for the two items and unordered lists to replace the codeboxes (unneccessary here).
* In Power, I have ensured each chemical battery type has its full name and common abbreviation in brackets.
* In Power, I have added two warning boxes to emphasise the dangers of lead-acid and Li-On batteries.
* In Power, some minor grammatical changes.
* Corrected "Psycology" typo in the Apps chapter.
* In Medicine, the figure 4-1 image is not available on the wiki, but is on the app. What's going on there?
* In Water, corrected "dehydrate" typo in the fluids table (I also need to get a proper table CSS class going there)
* In Food, added an ordered list for several lists that were marked with an asterisk including the fish poisoning list.
* In Food, why is each paragraph numbered? Have the paragraphs just been copied verbatim from the original US Army FM guide?
* In Desert, there are also paragraph numbers like with the Food chapter.
* In Tropical, the tree level diagram has 2 ordinal typos.
* In Tropical and Sea, reworded the "Chapter Water" and "Chapter Food" references to flow better in English.
* In Cold, there are also paragraph numbers.
* In Cold, the windchill table is so large I have made cover the whole width of the page.
* In Cold, changed the appearance of the 4 principles of keeping warm. Each letter is bold and separated from the paragraphs following it clearly. I plan on making these standout more.
* In Sea, changed the five As list from unordered to ordered.

* In MultiTool, added that it's also referred to as a penknife. Particularly in British English.