#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from __future__ import unicode_literals

import os
import os.path as op

AUTHOR = u'Alexandre Manhães Savio'
SITENAME = u'Interlines'
SITESUBTITLE = u'Lost in spikes'
#SITEURL = 'http://localhost:8000'
SITEURL = 'http://alexsavio.github.io'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = u'en_US'

#THEME = '../themes/pelican-bootstrap3'
#THEME = 'themes/notmyidea'
THEME = 'themes/purecollab'
COVER_IMG_URL = 'imgs/blog_wallpaper.jpg'
PROFILE_IMAGE_URL = 'imgs/logo_alone.svg'
TAGLINE = 'C/C++ developer, Python enthusiast and SysAdmin doing Data Analysis, Neuroscience and Medical Imaging'
#THEME = 'themes/pelican-elegant-1.3'
#THEME = 'themes/pure'

PDF_GENERATOR = True

OUTPUT_PATH = '../output'
DELETE_OUTPUT_DIRECTORY = False

PLUGIN_PATHS = [op.join(op.dirname(op.realpath(__file__)), 'plugins')]
PLUGINS = ['assets',
           'sitemap',
           'code_include',
           'ical',
           'gravatar',
           'feed_summary',
           'read_more_link',
           'render_math',
#           'liquid_tags',
           'optimize_images',
           'summary',
           'thumbnailer',
           'github_activity']

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
SOCIAL = (('Twitter', 'twitter-square', 'https://twitter.com/alex_savio'),
        ('GitHub', 'github', 'https://github.com/alexsavio'))

TWITTER_USERNAME = 'alex_savio'
GITHUB_URL = 'http://github.com/alexsavio'
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
MENUITEMS = [#('About', 'about.html'),
             ('About', 'http://www.ehu.es/ccwintco/index.php/Usuario:Alexsavio')]

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

GITHUB_ACTIVITY_MAX_ENTRIES = 5
