#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Alexandre M. S.'
SITENAME = u'Interlines'
SITESUBTITLE = u'Lost in spikes'
#SITEURL = 'http://localhost:8000'
SITEURL = 'http://alexsavio.github.io'

TIMEZONE = 'Europe/London'

DEFAULT_LANG = u'en_US'

#THEME = '../themes/pelican-bootstrap3'
THEME = 'themes/notmyidea'

PDF_GENERATOR = True

OUTPUT_PATH = '../output'
DELETE_OUTPUT_DIRECTORY = False

PLUGIN_PATH = 'plugins'
PLUGINS = ['assets', 'sitemap', 'code_include', 'ical', 
           'liquid_tags', 'optimize_images', 'summary', 'thumbnailer']

SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'daily',
        'indexes': 'daily',
        'pages': 'monthly'
    }
}

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = u'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = u'feeds/%s.atom.xml'
#TRANSLATION_FEED_ATOM = None

FEED_ALL_RSS = u'feeds/all.rss.xml'
CATEGORY_FEED_RSS = u'feeds/%s.rss.xml'

# Blogroll
LINKS =  (('BCIG.EU', 'http://bcig.eu/'),
          ('Pelican', 'http://getpelican.com/'),
          ('Python.org', 'http://python.org/'))

# Social widget
SOCIAL = (('twitter', 'http://twitter.com/alex_savio'),
          ('github', 'http://github.com/alexsavio'))

TWITTER_USERNAME = 'alex_savio'
GITHUB_URL = 'http://github.com/alexsavio'
GITHUB_ACTIVITY_FEED = 'https://github.com/alexsavio.atom'

#PAGINATION
DEFAULT_PAGINATION = 5
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
    '.nojekyll',]

#EXTRA_PATH_METADATA = {
#    'extra/robots.txt': {'path': 'robots.txt'},
#    }
#ARTICLE_URL = 'posts/{date:%Y}/{date:%b}/{date:%d}/{slug}/'
#ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%b}/{date:%d}/{slug}/index.html'


#TEMPLATE_PAGES = {'pages/about.md': 'about.html',}
#                  '/resume.': 'resume.html',
#                  'pages/contact.html': 'contact.html'}

# code blocks with line numbers
#PYGMENTS_RST_OPTIONS = {'linenos': 'table'}
PYGMENTS_RST_OPTIONS = {'classprefix': 'pgcss', 'linenos': 'table'}

#
MENUITEMS = [('About', 'about.html'),
             ('My CV', 'http://www.ehu.es/ccwintco/index.php/Usuario:Alexsavio')]

DATE_FORMATS = {
    'en_US': '%a, %d %b %Y',
}

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = False

DISPLAY_PAGES_ON_MENU = False
MD_EXTENSIONS = ['codehilite','extra']
MARKUP = ('rst', 'md', 'ipynb')

OUTPUT_SOURCES = 'True'
OUTPUT_SOURCES_EXTENSION = '.txt'

TYPOGRIFY = True

