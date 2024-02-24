# `ebookbuild.py` release notes

`ebookbuild.py` and `ebookbuild-3.3.py` are both licenced under the GNU General Public License v3 (GPLv3). GPLv3 is a strong copyleft licence so make sure you are familar and happy with it before contributing! 

Many of these will be petty modifications to make the source code more readable and provide a slightly better user experience (UX).

Pull requests are welcome! I am still learning Python 3 so I encourage improvements and I plan on it being a lot more elegant by being object-oriented and using the lxml library.

## v0.82.1

Added a Python list for specifying reflowable and fixed layouts. This makes specifying it more flexible. I still haven't tested fixed-layout in `ebookbuild` though.

* `reflowable = ["Reflowable", "reflowable", "reflow", "r"]`
* `fixed_layout = ["Fixed layout", "Fixed Layout", "fixed layout", "fixed", "f"]`

## v0.82

The Kindle Cover, Table of Contents and Start Reading are now optionally supported, just set the `"enableGuide" = "true"` boolean in the Metadata.json file.