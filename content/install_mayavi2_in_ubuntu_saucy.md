Title: Installing Mayavi2
Date: 2014-02-08 20:44:37
Category: Python
Tags: python, virtualenv, data
Slug: data-analysis-tools-install
Author: Alexandre M. Savio
Summary: Installing Python data analysis tools
Status: draft

## First approach: compile VTK

 Install WxGTK

    ```bash
    sudo apt-get install python-wxgtk2.8
    ln -s $lib_system_path/wx-2.8-gtk2-unicode $lib_virtualenv_path/wx-2.8-gtk2-unicode
    ```

 Install dev packages to compile VTK

    ```bash
    sudo apt-get install python-qt4-dev ccmake libgl1-mesa-dev libgl1-mesa-glx libglu1-mesa-dev libglw1-mesa-dev mesa-common-dev
    ```

 Download VTK from sources and build with CMake

  [VTk5.10.1](http://www.vtk.org/files/release/5.10/vtk-5.10.1.tar.gz)

  Configure it to install the python libraries and module in your virtualenv.

 Activate your virtualenv and install Envisage and Mayavi

    ```bash
    pip install envisage
    pip install mayavi
    ```

 ## Or install from the packages and remove the no-global-site-packages file from the virtualenv.

    ```bash
    sudo apt-get install python-vtk
    ```

  Activate your virtualenv and install Envisage and Mayavi

    ```bash
    pip install envisage
    rm $VIRTUAL_ENV/lib/python2.7/no-global-site-packages.txt
    pip install mayavi
    ```

### References

 1. https://github.com/enthought/traits/tree/master

 2. <http://calvinx.com/2012/11/03/ipython-qtconsole/>

 3. <https://gist.github.com/alexsavio/7580457>

 4. <http://davematthew.blogspot.com.es/2013/10/installing-matplotlib-and-mayavi-on-mac.html>
