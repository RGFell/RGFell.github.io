#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = 'Rodrigo Gomez-Fell'
SITENAME = 'The unimpressive Blog'
SITEURL = ''

PATH = 'content'
STATIC_PATHS = ['images']
TIMEZONE = 'Antarctica/McMurdo'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'
FEED_ALL_RSS = 'feeds/all.rss.xml'
AUTHOR_FEED_RSS = False
RSS_FEED_SUMMARY_ONLY = False
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None




# Blogroll
LINKS = (('Pelican', 'https://getpelican.com/'),
         ('Python.org', 'https://www.python.org/'),
         ('Jinja2', 'https://palletsprojects.com/p/jinja/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('LinkedIn', 'https://www.linkedin.com/in/rodrigogomezfell/'),
          ('Twitter(#RGFell)' , 'https://twitter.com/RGFell'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
