Title: Installing common Python data analysis tools in virtualenv
Date: 2014-04-26 18:38:37 
Category: Python
Tags: python, virtualenv, data
Slug: data-analysis-tools-install
Author: Alexandre M. Savio
Summary: Installing Python data analysis tools 

Tested on Ubuntu 13.10 and 14.04.

### Install needed packages:

   sudo apt-get install python-pip python-dev

   sudo pip install virtualenv virtualenvwrapper

   echo "export WORKON_HOME=~/envs" >> ~/.bashrc
   echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
   echo "export PIP_REQUIRE_VIRTUALENV=true" >> ~/.bashrc
   source ~/.bashrc

### Create a virtual environment

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

    sudo apt-get build-dep python-scipy

    sudo apt-get install libblas-dev liblapack-dev

    pip install scipy

 [Readline](http://docs.python.org/3.3/library/readline.html)

    sudo apt-get install libncurses5-dev

     pip install readline

 Other dependencies

    pip install python-dateutil sphinx pygments tornado

### Graphical libraries for GUI building and IPython QT console

#### You can either install them inside the virtual environment:

     pip install pyside

 PyQt4 must be installed globally:

     sudo apt-get install python3-pyqt4 python3-sip

 or

     sudo apt-get install python-pyqt4 python-sip


#### I recommend installing them globally then linking from the virtual environment:

 First install them:

    sudo apt-get install python3-qt4 python3-pyside python3-sip

 or

    sudo apt-get install python-qt4 python-pyside python-sip

 Then link them (with the virtualenv activated):

 In [3] we can see a script to link any library to the virtual environment (save
it in, e.g. symlink_pyqt4_and_sip.sh or ${WORKON_HOME}/postmkvirtualenv and
execute it):

    #!/bin/bash
    # This hook is run after a new virtualenv is activated.
    # ~/.virtualenvs/postmkvirtualenv

    function find_real_lib {
        syspy=$1
        libname=$2
        syspath=$($syspy -c "import sys; print(' '.join(sys.path).strip())")
        for libdir in $syspath; do
            if [ -e $libdir/$libname ]; then
                eval "$3=$libdir/$libname"
                return 0
            fi 
        done
        return 1
    }

    libs=( PyQt4 sip.so PySide sip.cpython-34m-x86_64-linux-gnu.so )
    #other_libs = ( vtk cairo )

    python_version=python$(python -c "import sys; print (str(sys.version_info[0])+'.'+str(sys.version_info[1]))")
    var=( $(which -a $python_version) )
    syspy=${var[-1]}

    get_python_lib_cmd="from distutils.sysconfig import get_python_lib; print (get_python_lib())"
    lib_virtualenv_path=$(python -c "$get_python_lib_cmd")

    for lib in ${libs[@]}
    do
        libsyspath=''
        find_real_lib $syspy $lib libsyspath
        if [ $? == '0' ]; then
            ln -s $libsyspath $lib_virtualenv_path/$lib
        fi
    done

### Other interesting modules

 [matplotlib](http://matplotlib.org/)

    sudo apt-get build-dep python-matplotlib

    pip install pyparsing

    pip install matplotlib

 [scikit-image](http://scikit-image.org/)

    pip install scikit-image

 [scikit-learn](http://scikit-learn.org)

    pip install scikit-learn

 [scikit-fuzzy](https://github.com/scikit-fuzzy/scikit-fuzzy)

 [Pandas](http://pandas.pydata.org/)

    sudo apt-get install libhdf5-dev

    pip install numexpr
    pip install tables

 If you have problems importing tables, it might help downloading and compiling the [HDF5 library](http://www.hdfgroup.org/HDF5/release/obtainsrc.html).

    pip install pandas

 [h5py](http://www.h5py.org/)

    sudo apt-get install libhdf5-dev

    pip install h5py

 [patsy](http://patsy.readthedocs.org/en/latest/) and [statsmodels](http://statsmodels.sourceforge.net/)

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


 [Nipy](http://nipy.org/) Dependencies:

    pip install sphinx sympy networkx traits

    pip install nipy

    pip install nipype dipy nitime

### References

 1. <http://www.cs.dartmouth.edu/~nfoti/blog/blog/2012/07/17/setting-up-
virtualenv-for-data-analysis-on-osx/>

 2. <http://calvinx.com/2012/11/03/ipython-qtconsole/>

 3. <https://gist.github.com/alexsavio/7580457>
