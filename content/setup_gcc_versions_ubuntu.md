Title: How to set up different versions of GCC
Date: 2014-06-03 11:00:00
Category: Ubuntu
Tags: ubuntu, gcc, config, update-alternatives
Slug: setup-gcc-versions
Author: Alexandre M. Savio
Summary: How to set up different versions of GCC


I usually need to change versions of software I use on Ubuntu, e.g., gcc and g++ 
and Java.

A very neat way to do it is using *update-alternatives*. This how you have to do it with gcc:

    sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.6 60 --slave /usr/bin/g++ g++ /usr/bin/g++-4.6
    sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.7 40 --slave /usr/bin/g++ g++ /usr/bin/g++-4.7
    sudo update-alternatives --config gcc

### References

[1] <http://charette.no-ip.com:81/programming/2011-12-24_GCCv47/>
