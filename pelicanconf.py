#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from __future__ import unicode_literals

import os
import os.path as op

AUTHOR = u'Alexandre Manhães Savio'
SITENAME = u'Interlines'
SITESUBTITLE = u'Lost in spikes'
SITEURL = 'https://alexsavio.github.io'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = u'en_US'

THEME = 'themes/pure'
COVER_IMG_URL = 'imgs/blog_wallpaper.jpeg'
PROFILE_IMAGE_URL = 'imgs/neurita.png'
TAGLINE = 'Software Engineer. IoT, DevOps, neuroimaging, machine-learning, Python and C/C++ coder. ACPySS  and EuroPython.'

PDF_GENERATOR = True

OUTPUT_PATH = 'output'
DELETE_OUTPUT_DIRECTORY = False

PLUGIN_PATHS = [op.join(op.dirname(op.realpath(__file__)), 'plugins')]
PLUGINS = [
    'assets',
    'sitemap',
    'code_include',
    'ical',
    'gravatar',
    'feed_summary',
    'read_more_link',
    'render_math',
    'liquid_tags',
    'optimize_images',
    'summary',
    'thumbnailer',
    'github_activity',
    'better_codeblock_line_numbering',
    'dateish',
]

SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5,
    },
    'changefreqs': {
        'articles': 'daily',
        'indexes': 'daily',
        'pages': 'monthly',
    },
}

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = u'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = u'feeds/{slug}.atom.xml'

FEED_ALL_RSS = u'feeds/all.rss.xml'
CATEGORY_FEED_RSS = u'feeds/{slug}.rss.xml'

# Blogroll
LINKS =  (
    ('Pelican', 'http://getpelican.com/'),
    ('Python.org', 'http://python.org/'),
)

# Social widget
SOCIAL = (
    ('twitter-square', 'https://twitter.com/alex_savio'),
    ('github', 'https://github.com/alexsavio'),
)

TWITTER_USERNAME = 'alex_savio'
GITHUB_URL = 'https://github.com/alexsavio'
GITHUB_ACTIVITY_FEED = 'https://github.com/alexsavio.atom'

#PAGINATION
DEFAULT_PAGINATION = 10
#PAGINATION_PATTERNS = (
#    (1, '{base_name}/', '{base_name}/index.html'),
#    (2, '{base_name}/page/{number}/', '{base_name}/page/{number}/index.html'),
#)

# Take advantage of the following defaults
# STATIC_SAVE_AS = '{path}'
# STATIC_URL = '{path}'
PATH = 'content'

STATIC_PATHS = [
    'imgs',
    'extra/robots.txt',
    'keybase.txt',
]


#TEMPLATE_PAGES = {'pages/about.md': 'about.html',}
#                  '/resume.': 'resume.html',
#                  'pages/contact.html': 'contact.html'}

# code blocks with line numbers
PYGMENTS_RST_OPTIONS = {'classprefix': 'pgcss', 'linenos': 'table'}

MENUITEMS = [#('About', 'about.html'),
            ('About Me', 'http://www.ehu.es/ccwintco/index.php?title=Usuario:Alexsavio'),
            ('ORCID', 'https://orcid.org/0000-0002-6608-6885'),
            ('Surf-Forecast', 'http://www.surf-forecast.com/breaks/Zarautz/forecasts/latest/six_day'),
]
DATE_FORMATS = {
    'en_US': '%a, %b %d %Y',
}

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = False

DISPLAY_PAGES_ON_MENU = True

MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
    },
    'output_format': 'html5',
}

MARKUP = ('rst', 'md', 'ipynb')

OUTPUT_SOURCES = 'True'
OUTPUT_SOURCES_EXTENSION = '.txt'

TYPOGRIFY = True

GITHUB_ACTIVITY_MAX_ENTRIES = 5
