Title: Compile Numpy and Scipy against Intel MKL
Date: 2014-04-08 22:00
Category: Python
Tags: Numpy, Scipy, MKL
Slug: numpy_scipy_mkl
Author: Alexandre Savio
Summary: Numpy and Scipy on Intel MKL

###### Tested on Ubuntu 13.10 and 14.04

### 1. Install C++ Composer and FORTRAN Composer, with MKL

  Fill forms and download online installation shell scripts from [here](http://software.intel.com/en-us/non-commercial-software-development).

### 2. Execute shell scripts with sudo

   I will assume the libraries will be installed in /opt/intel.

### 3. Once installed, add this to ~/.bashrc

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

- Change directory to numpy-x.x.x

- Create a site.cfg from the existing site.cfg.examle

- Edit site.cfg as follows:

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

- Modify cc_exe in numpy/distutils/intelccompiler.py to be something like:

<div class="codehilite"><pre>
self.cc_exe = \'icc -O3 -g -fPIC -fp-model strict -fomit-frame-pointer -openmp -xhost\' 
</div></pre>

- Here we use, -O3, optimizations for speed and enables more aggressive loop transformations such as Fusion, Block-Unroll-and-Jam, and collapsing IF statements, -openmp for OpenMP threading and -xhost option tells the compiler to generate instructions for the highest instruction set available on the compilation host processor. If you are using the ILP64 interface, please add -DMKL_ILP64 compiler flag.

- Run <code>icc --help</code> for more information on processor-specific options, and refer Intel Compiler documentation for more details on the various compiler flags.

- Modify the the Fortran compiler flags in numpy-x.x.x/numpy/distutil/fcompiler/intel.py to use the following compiler options for the Intel Fortran Compiler:

- For ia32 and Intel64

<div class="codehilite"><pre>
ifort -xhost -openmp -fp-model strict -fPIC
</div></pre>

- Modify the get_flags_opt function line to:

<div class="codehilite"><pre>
return ['-xhost -openmp -fp-model strict']
</div></pre>

If you are using ILP64 interface of Intel MKL, please add -i8 flag above.  If you are using older versions of Numpy/SciPy, please refer the new intel.py for your reference from the latest version of NumPy, which can be replaced to use the above mentioned compiler options.
                
### 7. Compile Numpy and Scipy with the following command (once for Numpy and then once for Scipy):

Remember to activate the virtual environment if you are going to use this in one.

#### 7.1 For 64-bit:

    cd <numpy-x.x.x>
    python setup.py config --compiler=intelem --fcompiler=intelem build_clib \
    --compiler=intelem --fcompiler=intelem build_ext --compiler=intelem --fcompiler=intelem install

    cd <scipy-x.x.x>
    python setup.py config --compiler=intelem --fcompiler=intelem build_clib \
    --compiler=intelem --fcompiler=intelem build_ext --compiler=intelem --fcompiler=intelem install

#### 7.2 For 32-bit:

    cd <numpy-x.x.x>
    python setup.py config --compiler=intel --fcompiler=intel build_clib \
    --compiler=intel --fcompiler=intel build_ext --compiler=intel --fcompiler=intel install

    cd <scipy-x.x.x>
    python setup.py config --compiler=intelem --fcompiler=intelem build_clib \
    --compiler=intelem --fcompiler=intelem build_ext --compiler=intelem --fcompiler=intelem install

### 8. Troubleshooting:

#### 8.1 Compiling Scipy: "Using deprecated NumPy API, disable it by..."

- Maybe it is the version of GCC, try using 4.7 (worked in November 2013):

<div class="codehilite"><pre>
    sudo apt-get install gcc-4.7
    sudo rm /usr/bin/gcc
    sudo ln -s /usr/bin/gcc-4.7 /usr/bin/gcc
</div></pre>

  Compile both Numpy and Scipy again.

