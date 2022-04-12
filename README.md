# SurvivalManual-ebook
An ePub (and eventual PDF) of the survival manual by Ligi, as requested by: https://github.com/ligi/SurvivalManual/issues/98

This project is a community-created survival manual based on the public domain [US Army Survival Field Manual FM 3-05.70 (FM 21-76)](https://fas.org/irp/doddir/army/fm3-05-70.pdf).

Content provided by: https://github.com/ligi/SurvivalManual

I have started this project by adding the wiki folder where I have used git clone to copy across the contents of the wiki. The wiki was last edited in 2020.

Much like Ligi's app, the survival manual is small at under 4.5MB in size for the ePub (usually Kindle books are larger for backward compatibility).

## Foreword

*“You’re not taking into consideration the most important human element of all; the will to live. Until a person is faced with death, it’s impossible to tell whether they have what it takes to survive.”*
— **John Kramer, Saw VI**

This is an effort to make Ligi’s survival manual more accessible by making it available as an ePub. The ePub is a popular e-book file format that can be read using popular apps such as Adobe Digital Editions and Google Play Books. Alternatively, the ePub file can also be converted to the Kindle format using Calibre or Kindle Previewer. The e-ink Kindle Paperwhite e-readers have a very long battery life that can last days or even weeks depending on usage. Its low power requirements are something to consider if you can get a generator working as described in the Power chapter.

The ultimate intention of this is project is to provide the survival manual as a printable PDF, then possibly as a physical book. A printed survival manual would be more practical because it does not require power and is more resilient to the elements. It is also unlikely to abruptly fail, which can happen to electronic devices such as a smartphone, tablet or e-reader.

I have included all the content from Ligi’s survival manual wiki as of last edit on the 5<sup>th</sup> February 2021. I want to maintain parity with the source as it gets updated with new or amended information – so do let me know if I am missing anything.

My own inspiration for this printed guide is the 2014 edition of the “SAS Survival Handbook: The Definitive Survival Guide” (ISBN: 978-0007595860) by John ‘Lofty’ Wiseman, a former SAS member and survival expert. In the preface the author explains is the importance of three key aspects neccessary for survival which are the skills you have learnt, the equipment you have (kit) and the will to live. This demonstrates the importance of having the correct mindset in a life or death situation.

The SAS Survival Guide is also useful for obtaining inspiration for creating effective typesetting for the survival manual. I like the typesetter’s use of grey boxes for showing important information and the circular icons on the contents page. An effective survival manual needs to be easy to read and all warnings should be easy to see.

## What's changed?

Most of the content will be kept the same though I plan on making minor alterations (see the ConversionNotes.md for more information). I have already changed the Psychology chapter icon for a more appropriate one, along with alterations to the typesetting. One image will likely be replaced with just a table.

Alongside providing content from Ligi's Android app, I want to improve the content at the same time by:

* Added a table of contents (TOC) because that's required for an e-book. (https://github.com/ligi/SurvivalManual/issues/92)
* Cropping, transcribing and annotating the text-heavy images including removing borders (https://github.com/ligi/SurvivalManual/issues/62) - The goal is to remove text from images to make the manual easier to translate and localise. I have already completed the Signaling chapter.
* Hand sanitiser recipe, a recipe I found on Telegram is added as a bonus chapter in the repo's "misc" folder. I have extracted the text from the WHO PDF (https://github.com/ligi/SurvivalManual/issues/97).

The icon source files are saved in the .afdesign format used by [Affinity Designer](https://affinity.serif.com/designer). I may move this over to [Inkscape](https://inkscape.org) to make the project more accessible.

## What's needed?

* A front cover image
~~* Add all the contents icons~~
* Apply alterations to upstream (the original guide's wiki)

## E-book

**The e-book can be compiled and is currently in testing.**

The ePub contents are in the e-book folder. The metadata.json holds the metadata that is used to create the content.opf and toc.ncx files. Currently, ebookbuild creates ePub 2.0.1 files (with plans to support the latest ePub 3 version in the future).

### Development

I use Visual Studio Code and formerly Atom to edit the XHTML, CSS and JSON files. Any text editor that supports regular expressions should be fine for e-book development, including `vim` and `emacs`.

### Compilation

The e-book metadata is added to the metadata.json file which is used by ebookbuild script to compile the book.

When I have finished the e-book it can be compiled. To compile the ePub, you will need to install both [Python 3](https://www.python.org/) to create the ePub and the [Java Development Kit (JDK)](https://www.oracle.com/uk/java/technologies/javase-downloads.html) to run epubcheck to verify it is up to standard.

Compile an ePub with the following command in Bash (I recommend installing WSL+Ubuntu for Windows 10 users) while in the e-book folder: `python3 ebookbuild.py && java -jar epubcheck.jar LigiSurvivalManual.epub`

An acceptable ePub for testing should have the `No errors or warnings detected` output from epubcheck.

### Testing

#### ePub

I recommend the following 2 ways of testing an ePub. Ideally the ePub should look good both in both readers:

* Upload the ePub to [Google Play Books](https://play.google.com/books) (requires Google Account) - This is great for reading on the go and I use it to hightlight and make note of any and all issues I have with the current ePub I am testing. The notes are automatically saved to a document on Google Drive even if the ePub is deleted, which I do when I have compiled a new version.
* Open the ePub in [Adobe Digital Editions](https://www.adobe.com/uk/solutions/ebook/digital-editions.html) (ADE) (available for Windows and Mac) - A popular ePub reader from Adobe (notable as it supports Adobe DRM) that is quite strict. Back when I first started e-book development I had to make sure the ePub looked perfect in ADE before submission to the client.

#### Kindle

I am prioritising the ePub as it's an open format and I like my approach to testing. Kindle books can be made in two ways and then sideloaded:

* Official - currently only [Kindle Previewer](https://kdp.amazon.com/en_US/help/topic/G202131170) (on Windows and macOS) is the official tool from Amazon to create Kindle books. The [`kindlegen`](https://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211) tool has been discontinued and is no longer available for download.
* Unofficial - the [Calibre](https://calibre-ebook.com/) library software includes extensive conversion tools that create the older .mobi files.

### Regular expressions

The files are manually edited using the free Microsoft Visual Studio Code text editor with regular expressions (regex). The syntax is identical to the Atom editor. The regex syntax used here is as follows:

* `(.+?)` the dot-plus-question mark combined will search any text and the brackets are used to save it into a register so that the text input can be put back when replaced
* `$1` the dollar symbol (or backslash in Notepad++) is used along with a number to retrieve the saved data in the register. Each pair of brackets represents another register.
* `\t` used to find or create a tabbed indentation (equivalent of pressing the tab key)
* `\n` used to find or create a newline (equivalent of pressing the return/enter key)
* `\s` used to find or create a space (equivalent of pressing the spacebar)
* `\` the backslash on its own is used to tell regex that you are manipulating an actual character, such as a `.`, `+`, `?`, `*`, `$`.

For each chapter I do the following:

1. I copy the XHTML declaration from line 1 to the first `<div>` tag on line 9.
2. Use regex to make every opening `<blockquote>` as a `<div>`.
3. Use regex to add the noindent top class to each `<p>` tag with this in the search, then replace: `<p>(.+?)</p>` `\t<p class="noindent top">$1</p>\n`
4. Use regex to add a tab and newline for the heading tags: `<h3 id="(.+?)">(.+?)</h3>` `\t<h3 id="$1">$2</h3>\n`
5. Use regex to add the images and fix the tags: `<p class="noindent top"><a name="(.+?)"></a><img src="(.+?)" alt="(.+?)" /></p>` `<p class="center top"><img id="$1" src="$2" alt="$3"/></p>`
6. Use regex to add the figure caption class below the images: `<p class="noindent top"><b>Figure(.+?)</b></p>` `<p class="figure-caption">Figure$1</p>`
7. Use regex to fix the bold `<strong>(.+?)</strong>` `<b>$1</b>` and italic `<em>(.+?)</em>` `<i>$1</i>` tags.
8. Use regex to fix the opening tag for unordered lists: `<ul>` `\t<ul>`
9.  Use regex to indent the list tags: `<li>` `\t\t<li>`
10. Use regex to fix the closing tag for unordered lists: `</ul>` `\t</ul>`
11. For chapters that have lists within paragraphs, escape the asterisk `\*\s(.+?)\.` and then add the list tags `<li>$1.</li>`
12. ...


## Licencing
The Google Material UI icons are licenced under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).

The app itself is licenced under [GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html) though I don't think that affects this project's files.

I have clarified with the developer that the survival manual's wiki content is in the public domain.

There is also a BSD-like disclaimer for the app:

>THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.