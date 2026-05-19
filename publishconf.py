#!/usr/bin/env python

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = "https://alexsavio.github.io"
RELATIVE_URLS = False

DELETE_OUTPUT_DIRECTORY = True

# Drafts must never reach the public web. Empty *_SAVE_AS tells Pelican to skip
# writing the file entirely (no HTML on disk → nothing deployed, nothing
# crawlable). Local `build` (pelicanconf) still renders drafts for preview.
DRAFT_SAVE_AS = ""
DRAFT_URL = ""
DRAFT_LANG_SAVE_AS = ""
DRAFT_LANG_URL = ""
DRAFT_PAGE_SAVE_AS = ""
DRAFT_PAGE_URL = ""
DRAFT_PAGE_LANG_SAVE_AS = ""
DRAFT_PAGE_LANG_URL = ""
