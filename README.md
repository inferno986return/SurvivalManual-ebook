# SurvivalManual-ebook
An ePub (and eventual PDF) of the survival manual by Ligi

This project is a community-created survival manual based on the public domain [US Army Survival Field Manual FM 3-05.70 (FM 21-76)](https://fas.org/irp/doddir/army/fm3-05-70.pdf).

Content provided by: https://github.com/ligi/SurvivalManual

I have started this project by adding the wiki folder where I have used git clone to copy across the contents of the wiki. The wiki was last edited in 2020.


## What's changed

Most of the content will be kept the same though I plan on making minor alterations (see the ConversionNotes.md for more information). I have already changed the Psychology chapter icon for a more appropriate one, along with alterations to the typesetting. One image will likely be replaced with just a table.

The icon source files are saved in the .afdesign format used by [Affinity Designer](https://affinity.serif.com/designer). I may move this over to [Inkscape](https://inkscape.org) to make the project more accessible.

## E-book

The ePub contents are in the e-book folder. The metadata.json hold the metadata that is used to create the content.opf and toc.ncx files. Currently, ebookbuild on creates ePub 2.0.1 files.

The files are manually edited using the free Microsoft Visual Studio Code text editor with regular expressions (regex). The syntax is identical to the Atom editor. The regex syntax used here is as follows:

* `(.+?)` the dot-plus-question mark combined will search any text and the brackets are used to save it into a register so that the text input can be put back when replaced
* `$1` the dollar symbol (or backslash in Notepad++) is used along with a number to retrieve the saved data in the register. Each pair of brackets represents another register.
* `\t` used to find or create a tabbed indentation (equivalent of pressing the tab key)
* `\n` used to find or create a newline (equivalent of pressing the return/enter key)
* `\s` used to find or create a space (equivalent of pressing the spacebar)
* `\` the backslash on its own is used to tell regex that you are manipulating an actual character, such as a `.`, `+`, `?`, `*`.

For each chapter I do the following:

1. I copy the XHTML declaration from line 1 to the first `<div>` tag on line 9.
2. Use regex to make every opening `<blockquote>` as a `<div>`.
3. Use regex to add the noindent top class to each `<p>` tag with this in the search, then replace: `<p>(.+?)</p>` `\t<p class="noindent top>$1</p>\n\n`
4. Use regex to add a tab for the heading tags: `<h3>` `\t<h3>`
5. Use regex to add the images and fix the tags:
6. Use regex to add the figure caption class below the images: `<p class="noindent top"><b>Figure(.+?)</b></p>` `<p class="figure-caption">Figure$1</p>`
7. Use regex to fix the bold `<strong>(.+?)</strong>` `<b>(.+?)</b>` and italic `<em>(.+?)</em>` `<i>(.+?)</i>` tags.
8. Use regex to fix the opening tag for unordered lists: `<ul>` `\t<ul>`
9. Use regex to indent the list tags: `<li>` `\t\t<li>`
10. Use regex to fix the closing tag for unordered lists: `</ul>` `\t</ul>`
11. For chapters that have lists within paragraphs, escape the asterisk `\*\s(.+?)\.` and then add the list tags `<li>$1.</li>`
12. ...

If you are unsure about something feel free to add it to the ConversionNotes.md, better yet try raising an issue on this repository!

When I have finished the e-book it can be compiled. To compile the ePub, you will need to install both [Python 3](https://www.python.org/) to create the ePub and the [Java Development Kit (JDK)](https://www.oracle.com/uk/java/technologies/javase-downloads.html) to run epubcheck to verify it is up to standard.

Compile an ePub with the following command in Bash (I recommend installing WSL+Ubuntu for Windows 10 users) while in the e-book folder: `python3 ebookbuild.py && java -jar epubcheck.jar LigiSurvivalManual.epub`


## Licencing
The Google Material UI icons are licenced under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).

The app itself is licenced under [GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).

The content looks to be licenced under a BSD-style licence, though I need to get this clarified by the original developer.

>THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.