# Conversion Notes
## General
* Initial conversion of MarkDown files to HTML via pandoc using this Bash command (courtesy of: https://www.dyrobooks.com/blog/2018/06/30/batch-convert-files-with-pandoc/ ): `for i in *.md ; do echo "$i" && pandoc -s $i -o $i.html ; done`
* Added icons to the Contents. I exported them from the [Material site](https://fonts.google.com/icons) as filled white icons in the .svg format that are 36dp in size. Looks good with the icon at 36px (tall, or wide for icons that are wider than they are tall) and exported to 50px (squared) in total size. Google add whitespace around the perimeter of each icon so I remove that and make the icons themselves 36px, then snap the icon to the exact centre of the black circle. These icons are a work-in-progress and feedback is welcome.
* Changed Food icon inadvertantly. I think the new icon is superior, so I am keeping it.
* Added coloured boxes for warning and caution text throughout the book.
* Made the tables consistent throughout the book.
* All the headings will need to be made consistent, I am using the original FM guide to assist with this. They are of mixed case.
* Need to replace inappropriate hyphens with en dashes.
* Need to re-add the Amazon affiliate links in the frontmatter.
* Removed `<img class="cover-image" src="images/cover.png" alt=""/>` from bookcover. Need to make a JPG cover image.

## Chapter specific
* In Introduction, grammatical changes such as removing hyphen from "re-install"
* In Power, removed hyphens and replaced with appropriate en dashes.
* In Power, I have used an ordered list at the top for the two items and unordered lists to replace the codeboxes (unneccessary here).
* In Power, made ordinals superscript and made the squared 2, as a superscript 2 because it's easier to read.
* In Power, I have ensured each chemical battery type has its full name and common abbreviation in brackets.
* In Power, I have added two warning boxes to emphasise the dangers of lead-acid and Li-On batteries.
* In Power, some minor grammatical changes. Infact I would recommend using Grammarly on this chapter at the upstream.
* In Power, expanded "reportedly 6h" to "reportedly within 6 hours" which is clearer to me.
* In Apps, corrected "Psycology" typo.
* In Apps, replaced hyphens with appropriate en dashes.
* In Apps, added that Morse signal is also known as Morse code.
* In Apps, added a morse code chart from Wikipedia (and attributed as public domain). Its 372px wide, close to the 350px that many of the other diagrams have.
* In Apps, made SOS morse code bold and replaced full-stops with bullet symbols, then hyphens with em dashes.
* In Apps, replaced ASIN for the BioLight camp stove to: B01FWRICY6
* In Kit, removed hyphen from "Multi-Tool", also consistent with appendix.
* In Kit, added Amazon link for LifeStraw (ASIN: B07C56LR6N).
* ~~In Medicine, the figure 4-1 image is not available on the wiki, but is on the app. What's going on there?~~
* In Medicine, added a nested list to step 4 of the open airway steps. Looks more readable.
* In Medicine, replaced poisonous with venomous. A poisonous animal is deadly when consumed or touched, a venomous animal has a deadly bite.
* In Water, corrected "dehydrate" typo in the fluids table (I also need to get a proper table CSS class going there)
* In Food, added an ordered list for several lists that were marked with an asterisk including the fish poisoning list.
* In Food, why is each paragraph numbered? Have the paragraphs just been copied verbatim from the original US Army FM guide? Some numbered paragraphs are hyperlinked so I'll leave them.
* In Plants, no Fig9-5.
* In Plants, assigned id="fig9-6" attribute to list for edible plants. Should make this into a table for consistency.
* In Desert, there are also paragraph numbers like with the Food chapter.
* In Tropical, the tree level diagram has 2 ordinal typos.
* In Tropical and Sea, reworded the "Chapter Water" and "Chapter Food" references to flow better in English. Need to make sure this consistent throughout the book.
* In Cold, found a typo for "injured" in the Frostbite table.
* In Cold, there are also paragraph numbers.
* In Cold, the windchill table is so large I have made cover the whole width of the page.
* In Cold, changed the appearance of the 4 principles of keeping warm. Each letter is bold and separated from the paragraphs following it clearly. I plan on making these standout more.
* In Cold, added space for "water purifying".
* In Sea, made the "five As" bold.
* In Sea, changed the five As list from unordered to ordered. Then used the acrostic class I made to make them stand out, then added an en dash with the keyword spaced from the accompanying explanation sentence.
* In Sea, corrected the sea snake and eel bites as being venomous. Clint's Reptiles has a good explanation for the difference between poisonous (if you bite it) and venomous (if it bites you).
* In Direction Finding, removed the "Step 1" part and replaced with ordered list, which is easier to read and less characters.
* In Direction Finding, capitalised "Volts" as with any unit named after a scientist.
* In Signaling, transcribed the signaling image into the text. Makes it a lot clearer (and searchable).
* In Self-Defense, moved summary to a whitebox. Looks pretty good.
* In Man-Made Hazards, added acronym for NATO.
* In Credits, minor grammatical changes such as adding a full-stop to the last paragraph and removing spaces between parantheses.

### Appendices
* In Multi-Tool, made the headings consistent.
* In Multi-Tool added corkscrew to list.
* In Multi-Tool, added that it's also referred to as a penknife. Particularly in British English. Also made "recommendation" lowercase and capitalised "Swiss". Plus grammatical changes.
* In Multi-Tool, made inappropriate hyphens as en dashes.
* In Multi-Tool, need to re-add the affiliate links as they aren't in the MarkDown, but they are in the app.
* In FAQ, added the full name as "Frequently Asked Questions (FAQ)".
* In FAQ, replaced hyphens with appropriate en dashes using regex: `\s-\s`
* In FAQ, capitalised Samsung as it's a proper noun.
* In Poisonous Plants, add the scientific names in italics.
* In Poisonous Plants, would be better to add a table with a description of what these plants are and where they are found in the world.
* In Poisonous Plants, added the foxglove to poisonous via ingestion section. I should also add the hogweed plant.
* Comparing this Poisonous Plants chapter to the FM original shows descriptions and images, as well as more plants. More information should be taken from there.
* In Translator Notes, tidied up some grammar and replaced hyphens with en dashes.
* In Hand Sanitizer, tried condensing the WHO document by combining the formulation and recommended quantities into one table.
* Added Further Reading section as a reference on all books mentioned in this survival guide.