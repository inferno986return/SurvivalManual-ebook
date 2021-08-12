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

The files are manually edited using the free Microsoft Visual Studio Code text editor with regular expressions. The syntax is identical to the Atom editor. For each chapter I copy the from line 1 to the first `<div>` tag.

When I have finished the e-book it can be compiled. To compile the ePub, you will need to install both [Python 3](https://www.python.org/) to create the ePub and the [Java Development Kit (JDK)](https://www.oracle.com/uk/java/technologies/javase-downloads.html) to run epubcheck to verify it is up to standard.

Compile an ePub with the following command in Bash (I recommend WSL+Ubuntu for Windows users) while in the e-book folder: `python3 ebookbuild.py && java -jar epubcheck.jar LigiSurvivalManual.epub`


## Licencing
The Google Material UI icons are licenced under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).

The app itself is licenced under [GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).

The content looks to be licenced under a BSD-style licence, though I need to get this clarified by the original developer.

>THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.