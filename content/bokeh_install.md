Title: Install Bokeh from sources
Date: 2014-11-11 22:11:46
Category: Python
Tags: python, plots, install
Slug: quick-bokeh
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: A short guide to install Bokeh from sources in a virtualenv on Ubuntu 14.04

# Introduction

Bokeh is a Python interactive visualization library that targets modern web browsers for presentation. You can find its home at http://bokeh.pydata.org/

There is a great gallery here: http://bokeh.pydata.org/docs/gallery.html#gallery

# Requirements

    sudo apt-get install nodejs npm redis-server

**Note:** activate your virtualenv now, if you wish.

    pip install numpy
    pip install flask redis requests pandas wsaccel ujson cython

## gevent

### Python 2.7

    pip install gevent

### Python 3.4

The current version of gevent at https://github.com/gevent/gevent is not compatible with Python 3 yet.
Luckily there is a fork of gevent patched to work with Python 3:

    git clone https://github.com/fantix/gevent.git
    cd gevent

    python setup.py install

## gevent-websocket

### Python 2.7

    pip install gevent-websocket

### Python 3.4

    hg clone https://bitbucket.org/Jeffrey/gevent-websocket
    cd gevent-websocket
    python setup.py install

# Clone Bokeh repository

    git clone https://github.com/bokeh/bokeh.git

## BokehJS

### Requirements

    cd bokeh/bokehjs
    npm install

### Install Grunt, the javascript task runner

    sudo npm install -g grunt-cli

### Deploy

Generate the compiled and optimized BokehJS libraries, and deploy them to the build subdirectory.

    grunt deploy

### Build

This will build the BokehJS sources without concatenating and optimizing into standalone libraries.

    grunt build

At this point you can use BokehJS together with require.js as an AMD module.

# Install Bokeh

    cd <wherever_is>/bokeh
    python setup.py install

This instruction will first ask if you want (1) a newly built BokehJS or (2) the build you just did in the **bokehjs** folder. Choose 2.

# Documentation

## Requirements

    pip install docutils sphinx sphinxcontrib-napoleon sphinx_bootstrap_theme sphinxcontrib-httpdomain

## Download sample data

    python -c 'import bokeh; bokeh.sampledata.download()'

## Build html

    cd <wherever_is>/bokeh/sphinx
    make html

### References

1. <http://bokeh.pydata.org/docs/installation.html>
