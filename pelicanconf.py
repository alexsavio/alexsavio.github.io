#!/usr/bin/env python

from pathlib import Path

VERSION = "1.0.0"

AUTHOR = "Alexandre Manhães Savio"
SITENAME = "Alexandre Manhães Savio"
SITESUBTITLE = "Freelance Software, Cloud & AI Engineer"
SITEDESCRIPTION = (
    "Freelance engineer building software, cloud and AI systems for R&D-heavy teams. "
    "Ex-academia with 8+ years in medical imaging and machine learning."
)
SITE_AVAILABILITY = "Accepting new engagements for Q2 2026"
SITEURL = ""  # Set to production URL in publishconf.py

TIMEZONE = "Europe/Paris"

DEFAULT_LANG = "en_US"

THEME = "themes/fancy-terminal"
THEME_LIGHT_MODE = True  # Use light burgundy theme

# Terminal prompt customization
TERMINAL_USER = "alex"
TERMINAL_HOST = "blog"
TERMINAL_TITLE = "zsh"

# Theme colors (Catppuccin Latte - https://catppuccin.com/palette/)
THEME_COLORS = {
    'bg_color': '#e6e9ef',        # Mantle
    'terminal_bg': '#eff1f5',     # Base
    'text_color': '#4c4f69',      # Text
    'primary_color': '#1e66f5',   # Blue
    'accent_color': '#8839ef',    # Mauve
    'muted_color': '#6c6f85',     # Subtext 0
    'code_bg': '#ccd0da',         # Surface 0
    'link_color': '#179299',      # Teal
    'header_bg': '#dce0e8',       # Crust
}

COVER_IMG_URL = "imgs/blog_wallpaper.jpeg"
PROFILE_IMAGE_URL = "imgs/alex_headshot.png"
OG_DEFAULT_IMAGE = "imgs/alex_headshot.png"
TAGLINE = "Freelance Software, Cloud & AI Engineer. Ex-academia (neuroimaging, ML). ACPySS and ex-EuroPython."

PDF_GENERATOR = True

OUTPUT_PATH = "output"
DELETE_OUTPUT_DIRECTORY = False

PLUGIN_PATHS = [str(Path(__file__).resolve().parent / "plugins")]
PLUGINS = [
    "assets",
    "sitemap",
    "code_include",
    "ical",
    "gravatar",
    "feed_summary",
    "read_more_link",
    "render_math",
    "liquid_tags",
    "optimize_images",
    "summary",
    "thumbnailer",
    "github_activity",
    "better_codeblock_line_numbering",
    "dateish",
]

SITEMAP = {
    "format": "xml",
    "priorities": {
        "articles": 0.5,
        "indexes": 0.5,
        "pages": 0.5,
    },
    "changefreqs": {
        "articles": "daily",
        "indexes": "daily",
        "pages": "monthly",
    },
}

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/{slug}.atom.xml"

FEED_ALL_RSS = "feeds/all.rss.xml"
CATEGORY_FEED_RSS = "feeds/{slug}.rss.xml"

# Blogroll — intentionally empty; real links live in SOCIAL + MENUITEMS.
LINKS = ()

# Contact
CONTACT_EMAIL = "alexsavio@gmail.com"

# Social links (name, url) — name is also used as a short label in the footer.
SOCIAL = (
    ("GitHub", "https://github.com/alexsavio"),
    ("LinkedIn", "https://www.linkedin.com/in/alexsavio/"),
    ("ORCID", "https://orcid.org/0000-0002-6608-6885"),
    ("RSS", "/feeds/all.atom.xml"),
)

GITHUB_URL = "https://github.com/alexsavio"
GITHUB_ACTIVITY_FEED = "https://github.com/alexsavio.atom"

# PAGINATION
DEFAULT_PAGINATION = 10
# PAGINATION_PATTERNS = (
#    (1, '{base_name}/', '{base_name}/index.html'),
#    (2, '{base_name}/page/{number}/', '{base_name}/page/{number}/index.html'),
# )

# Take advantage of the following defaults
# STATIC_SAVE_AS = '{path}'
# STATIC_URL = '{path}'
PATH = "content"
PAGE_PATHS = ["pages"]

STATIC_PATHS = [
    "imgs",
    "extra/robots.txt",
    "keybase.txt",
]

# code blocks with line numbers
PYGMENTS_RST_OPTIONS = {"classprefix": "pgcss", "linenos": "table"}

# Menu is driven by DISPLAY_PAGES_ON_MENU (about, work-with-me)
# plus the items below for non-page destinations.
# Note: SITEURL is prepended in the template for menu items, so use relative paths here.
MENUITEMS = []
DISPLAY_CATEGORIES_ON_MENU = False
DATE_FORMATS = {
    "en_US": "%a, %b %d %Y",
}

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = False

DISPLAY_PAGES_ON_MENU = True

MARKDOWN = {
    "extension_configs": {
        "markdown.extensions.codehilite": {"css_class": "highlight"},
        "markdown.extensions.extra": {},
        "markdown.extensions.meta": {},
    },
    "output_format": "html5",
}

MARKUP = ("rst", "md", "ipynb")

OUTPUT_SOURCES = "True"
OUTPUT_SOURCES_EXTENSION = ".txt"

TYPOGRIFY = True

GITHUB_ACTIVITY_MAX_ENTRIES = 5
