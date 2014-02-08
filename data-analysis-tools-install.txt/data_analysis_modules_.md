Title: Installing common Python data analysis tools in virtualenv
Date: 2014-02-08 20:44:37 
Category: Python
Tags: python, virtualenv, data
Slug: data-analysis-tools-install
Author: Alexandre M. Savio
Summary: Installing Python data analysis tools 


### First create virtual environment

    mkvirtualenv <env_name> -p <path_to_python>*

    *<path_to_python> can be either /usr/bin/python2 or /usr/bin/python3,
    or whatever you need.

### Install modules

 [IPython](http://ipython.org/)

    pip install ipython[all]

 [Numpy](http://www.numpy.org/)

    pip install numpy

 Test numpy

    pip install nose

    python -c 'import numpy; numpy.test()'

 [Cython](http://cython.org/)

    pip install cython

 [Scipy](http://www.scipy.org/)

    pip install scipy

 [Readline](http://docs.python.org/3.3/library/readline.html)

     easy_install readline

 Other dependencies

    pip install python-dateutil sphinx pygments tornado

### Graphical libraries for GUI building and IPython QT console

#### You can either install them inside the virtual environment:

     pip install pyside

 PyQt4 must be installed globally:

     sudo apt-get install python3-pyqt4

 or

     sudo apt-get install python-pyqt4


#### We recommend installing them globally then linking from the virtual
environment:

 First install them:

    sudo pip3 install pyside

    sudo apt-get install python3-qt4

 or

    sudo pip install pyside

    sudo apt-get install python-qt4

 Then link them (with the virtualenv activated):

 In [3] we can see a script to link any library to the virtual environment (save
it in, e.g. symlink_pyqt4_and_sip.sh or ${WORKON_HOME}/postmkvirtualenv and
execute it):

    #!/bin/bash
    # This hook is run after a new virtualenv is activated.
    # ~/.virtualenvs/postmkvirtualenv
     
    libs=( PyQt4 sip.so PySide )
     
    python_version=python$(python -c "import sys; print (str(sys.version_info[0])+'.'+str(sys.version_info[1]))")
    var=( $(which -a $python_version) )
     
    get_python_lib_cmd="from distutils.sysconfig import get_python_lib; print (get_python_lib())"
    lib_virtualenv_path=$(python -c "$get_python_lib_cmd")
    lib_system_path=$(${var[-1]} -c "$get_python_lib_cmd")
     
    for lib in ${libs[@]}
    do
    ln -s $lib_system_path/$lib $lib_virtualenv_path/$lib
    done

### Other interesting modules

 [matplotlib](http://matplotlib.org/)

    pip install matplotlib

 [scikit-image](http://scikit-image.org/)

    pip install scikit-image

 [scikit-learn](http://scikit-learn.org)

    pip install scikit-learn

 [scikit-fuzzy](https://github.com/scikit-fuzzy/scikit-fuzzy)

 [Pandas](http://pandas.pydata.org/)

    pip install numexpr
    pip install h5py
    pip install tables

 If you have problems importing tables, you might need to download and compile
hdf5 library:
<http://www.hdfgroup.org/HDF5/release/obtainsrc.html>

    pip install pandas

 [statsmodels](http://statsmodels.sourceforge.net/)

    pip install patsy
    pip install statsmodels

 [pymc](http://pymc-devs.github.io/pymc/)

    pip install pymc

### Speed up execution

 [bottleneck](https://pypi.python.org/pypi/Bottleneck)

    pip install bottleneck

 [cythongsl](https://github.com/twiecki/CythonGSL)
 [cythongsl-demo](http://nbviewer.ipython.org/github/twiecki/CythonGSL/blob/master/examples/cython_gsl_ipythonnb.ipynb)

    pip install cythongsl

### Neuroscience tools:

 [Nibabel](http://nipy.org/nibabel/)

    pip install nibabel


 [Nipy](http://nipy.org/)* Dependencies:

    pip install sphinx sympy networkx traits

    pip install nipy

    pip install nipype dipy nitime


(\*) These tools only work on Python 2.* (in time of writing Feb 8th 2014):

### References

 1. <http://www.cs.dartmouth.edu/~nfoti/blog/blog/2012/07/17/setting-up-
virtualenv-for-data-analysis-on-osx/>

 2. <http://calvinx.com/2012/11/03/ipython-qtconsole/>

 3. <https://gist.github.com/alexsavio/7580457>
