Title: Compile Numpy and Scipy against Intel MKL
Date: 2014-04-08 22:00
Category: Python
Tags: Numpy, Scipy, MKL, Python, OpenBLAS
Slug: numpy_scipy_mkl
Author: Alexandre Savio
Email: alexsavio@gmail.com
Summary: Numpy and Scipy on Intel MKL

###### Tested on Ubuntu 13.10 and 14.04

### 1. Install C++ Composer and FORTRAN Composer, with MKL

  Fill forms and download online installation shell scripts from [here](http://software.intel.com/en-us/non-commercial-software-development).

#### OpenBLAS Note

  If you want to use OpenBLAS as well, install it and follow the OpenBLAS notes along this tutorial.
  This has not been tested yet.

  But first, install it:

    :::bash
    git clone git://github.com/xianyi/OpenBLAS
    cd OpenBLAS && make FC=gfortran
    sudo make PREFIX=/opt/OpenBLAS install
    sudo ldconfig


### 2. Execute shell scripts with sudo

   I will assume the libraries will be installed in /opt/intel.

### 3. Once installed, add this to ~/.bashrc

    :::bash
    #Intel C++ Studio
    if [ -d /opt/intel ];
    then
        export INTEL_HOME=/opt/intel
        export PATH=${PATH}:${INTEL_HOME}/bin
        export LD_LIBRARY_PATH=/opt/intel/mkl/lib/intel64:/opt/intel/lib/intel64:${LD_LIBRARY_PATH}
    fi

### 4. Add this to /etc/ld.so.conf.d/intel.conf:

    /opt/intel/lib/intel64
    /opt/intel/lib/intel64/irml
    /opt/intel/lib/intel64/crt
    /opt/intel/mkl/lib/intel64

### 5. Download Numpy and Scipy from [here](http://www.scipy.org/scipylib/download.html)

### 6. Modify Numpy source code:

Change directory to numpy-x.x.x

Create a site.cfg from the existing site.cfg.examle

Edit site.cfg as follows:

Add the following lines to site.cfg in your top level NumPy directory to use Intel® MKL, if you are building on Intel 64 platform, assuming the default path for the Intel MKL installation from the Intel Parallel Studio XE 2013 or Intel Composer XE 2013 versions:

    [mkl]
    library_dirs = /opt/intel/mkl/lib/intel64
    include_dirs = /opt/intel/mkl/include
    mkl_libs = mkl_rt
    lapack_libs =

If you are building NumPy for 32 bit, please add as the following:

    [mkl]
    library_dirs = /opt/intel/mkl/lib/ia32
    include_dirs = /opt/intel/mkl/include
    mkl_libs = mkl_rt
    lapack_libs =

Modify cc_exe in numpy/distutils/intelccompiler.py to be something like:

    :::python
    self.cc_exe = \'icc -O3 -g -fPIC -fp-model strict -fomit-frame-pointer -openmp -xhost\'

Here we use, -O3, optimizations for speed and enables more aggressive loop transformations such as Fusion, Block-Unroll-and-Jam, and collapsing IF statements, -openmp for OpenMP threading and -xhost option tells the compiler to generate instructions for the highest instruction set available on the compilation host processor. If you are using the ILP64 interface, please add -DMKL_ILP64 compiler flag.

Run <code>icc --help</code> for more information on processor-specific options, and refer Intel Compiler documentation for more details on the various compiler flags.

Modify the the Fortran compiler flags in numpy-x.x.x/numpy/distutil/fcompiler/intel.py to use the following compiler options for the Intel Fortran Compiler:

For ia32 and Intel64

    :::bash
    ifort -xhost -openmp -fp-model strict -fPIC

Modify the get_flags_opt function line to:

    :::python
    return ['-xhost -openmp -fp-model strict']

If you are using ILP64 interface of Intel MKL, please add -i8 flag above.  If you are using older versions of Numpy/SciPy, please refer the new intel.py for your reference from the latest version of NumPy, which can be replaced to use the above mentioned compiler options.


#### OpenBLAS Note

To use OpenBLAS, uncomment the following lines and correct the paths:

    [openblas]
    libraries = openblas
    library_dirs = /opt/OpenBLAS/lib
    include_dirs = /opt/OpenBLAS/include


### 7. Check your config

    cd <numpy-x.x.x>
    python setup.py config

You should see the MKL library paths, and OpenBLAS if you enabled it.


### 8. Compile Numpy and Scipy with the following command (once for Numpy and then once for Scipy):

Remember to activate the virtual environment if you are going to use this in one.

#### 8.1 For 64-bit:

    :::bash
    cd <numpy-x.x.x>
    python setup.py config --compiler=intelem --fcompiler=intelem build_clib \
    --compiler=intelem --fcompiler=intelem build_ext --compiler=intelem --fcompiler=intelem install

    cd <scipy-x.x.x>
    python setup.py config --compiler=intelem --fcompiler=intelem build_clib \
    --compiler=intelem --fcompiler=intelem build_ext --compiler=intelem --fcompiler=intelem install

#### 8.2 For 32-bit:

    :::bash
    cd <numpy-x.x.x>
    python setup.py config --compiler=intel --fcompiler=intel build_clib \
    --compiler=intel --fcompiler=intel build_ext --compiler=intel --fcompiler=intel install

    cd <scipy-x.x.x>
    python setup.py config --compiler=intel --fcompiler=intel build_clib \
    --compiler=intel --fcompiler=intel build_ext --compiler=intel --fcompiler=intel install

### 9. Troubleshooting:

#### 9.1 Compiling Scipy: "Using deprecated NumPy API, disable it by..."

Maybe it is the version of GCC, try using 4.7 (worked in November 2013):

    :::bash
    sudo apt-get install gcc-4.7
    sudo rm /usr/bin/gcc
    sudo ln -s /usr/bin/gcc-4.7 /usr/bin/gcc

Compile both Numpy and Scipy again.


### 10. Testing

You can test OpenBLAS with the following code (got from <https://gist.github.com/osdf/>):

    :::python
    #!/usr/bin/env python
    import numpy
    import sys
    import timeit

    try:
        import numpy.core._dotblas
        print 'FAST BLAS'
    except ImportError:
        print 'slow blas'

    print "version:", numpy.__version__
    print "maxint:", sys.maxint
    print

    x = numpy.random.random((1000,1000))

    setup = "import numpy; x = numpy.random.random((1000,1000))"
    count = 5

    t = timeit.Timer("numpy.dot(x, x.T)", setup=setup)
    print "dot:", t.timeit(count)/count, "sec"



### References

1. <https://software.intel.com/en-us/articles/numpyscipy-with-intel-mkl>

2. <http://gehrcke.de/2014/02/building-numpy-and-scipy-with-intel-compilers-and-intel-mkl-on-a-64-bit-machine/>

3. <http://stackoverflow.com/questions/11443302/compiling-numpy-with-openblas-integration>

4. <https://gist.githubusercontent.com/osdf/3842524/raw/df01f7fa9d849bec353d6ab03eae0c1ee68f1538/test_numpy.py>
