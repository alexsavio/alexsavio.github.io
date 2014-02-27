Title: Using BibLatex with Lyx and JabRef
Date: 2014-02-27 18:11:46 
Category: LaTex
Tags: latex, lyx, bibtex
Slug: biblatex_lyx_jabref_encoding
Author: Alexandre M. Savio
Summary: Configuring BibLatex in Lyx to benefit of UTF-8 encoding

### Introduction

For publishing articles with Lyx I've used Zotero, JabRef and Lyx during my PhD.
I've always had problems with the encoding of the BibTex files and ended up
editing them in JabRef, removing/replacing strange characters.

Today a good friend indicated me [BibLatex](http://www.ctan.org/pkg/biblatex).
And we saw that Lyx could be configured to use it through 
[biber](http://biblatex-biber.sourceforge.net/).

This is a list of steps that you should perform in order to be able to use
BibLatex on Lyx.

### Step 1: Reconfigure encodings in Zotero and JabRef

Setup Zotero to export to UTF-8.

Setup JabRef to use the default encoding as UTF-8.


### Step 2: Install biblatex and biber

In Ubuntu I installed the packages: *biblatex texlive-latex-extra texlive-bibtex-extra*


### Step 3: Create the biblatex.module file

Create a file named biblatex.module with the following content:

    #\DeclareLyXModule{Biblatex-citation-styles}
    #DescriptionBegin
    #A prerequisite for using the biblatex package. This module simply
    #enables the author/year citation styles without actually loading natbib.
    #Biblatex itself needs to be loaded manually. Cf.
    #http://wiki.lyx.org/BibTeX/Biblatex
    #DescriptionEnd

    Format 11

    # this is biblatex actually
    Provides natbib    1


Put the file biblatex.module in the layouts folder in your user directory 
(Help→About LyX tells you where you can find this directory; in the latest versions of OSX the correct layouts folder is in the applications folder).

In Ubuntu it is ~/.lyx

Run Tools→Reconfigure, restart LyX.


### Step 4: Creating the .lyx file


#### Add the biblatex module

Add to "Selected" the module "Biblatex-citation-styles" from Document→Settings→Modules. 


#### Load biblatex in the preamble

In the document preamble (Document→Settings→Preamble) you have to load biblatex manually, with:

    \usepackage[natbib=true,style=numeric,backend=biber,maxnames=1, doi=true, url=false,bibencoding=utf8]{biblatex}


#### Load the bibliography in the preamble

Load your bibliography database in the preamble:

    \addbibresource{/home/alexandre/mybibs.bib}

Multiple databases must be loaded by multiple \addbibresource commands.

Please refer to the [biblatex documentation](http://mirrors.ctan.org/macros/latex/contrib/biblatex/doc/biblatex.pdf) for further options. 


#### Load the bibliography in a note

In the document, insert the BibTeX inset (Insert→List/TOC→BibTeX Bibliography... ) in a LyX note or comment, 
such that LyX finds the citations, but no \bibliography command is output to LaTeX. 

It does not matter which style you chose here, so you can stick with "plain". 
However, in order to use the citation dialog, you'll have to choose the correct databases (i.e. those you loaded above in item (3)).

This is only needed if you are going to use the citation dialog. I use JabRef to push the citations instead.


#### Put the printbibliography command

In the document, enter \printbibliography in ERT (TeX mode) at the place where the bibliography shall occur. 


#### View the file in PDF

And this should do it.


### References

1. <http://wiki.lyx.org/BibTeX/Tips>

2. <http://wiki.lyx.org/BibTeX/Biblatex>

3. <http://wiki.lyx.org/BibTeX/BiblatexStyles>

4. The biblatex.module file: <http://wiki.lyx.org/uploads/BibTeX/biblatex.module>

5. The bibtexall script: <http://wiki.lyx.org/uploads/BibTeX/bibtexall>

