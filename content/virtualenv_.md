Title: How to create virtualenvs with Virtualenvwrapper
Date: 2014-02-08 21:16:14
Category: Python
Tags: python, virtualenv, install
Slug: virtualenvwrapper
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: Create virtualenvs with virtualenvwrapper

## Virtualenv and virtualenvwrapper

 Install virtualenv and virtualenvwrapper

    sudo apt-get install python3-pip
    sudo pip3 install virtualenv virtualenvwrapper

 Virtualenvwrapper .bashrc setup:

    echo "export WORKON_HOME=~/envs" >> ~/.bashrc
    echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
    echo "export PIP_REQUIRE_VIRTUALENV=true" >> ~/.bashrc
    source ~/.bashrc


## Basic usage commands

 Create a virtualenv:

     mkvirtualenv <env name>

 Activate a virtualenv:

      workon <env name>

 Install a package in the activated virtualenv

    pip install <package name>

 Go to its directory when it is activated

    cdvirtualenv

 Set a working directory as a project of the virtualenv

    cd <project dir>
    setvirtualenvproject $VIRTUAL_ENV $(pwd)

 Get a list of the Python modules and versions installed in an activated
virtualenv

    pip freeze

 To deactivate a virtualenv

    deactivate

#### Run ipython within the virtualenv:

    alias ipy=\"python -c 'import IPython;
IPython.terminal.ipapp.launch_new_instance()'\"
    ipy

#### Run ipython with other options:

 Add this to .bashrc:

    alias ipy="python -c 'import IPython;
IPython.terminal.ipapp.launch_new_instance()'"

    function ipyqt(){
        python -c 'import IPython;
IPython.start_ipython(['"'"'qtconsole'"'"']);'
    }

    function ipynote(){
        python -c 'import IPython; IPython.start_ipython(['"'"'notebook'"'"']);'
    }

## Another interesting option:

 Download a virtualenv script:

    wget https://raw.github.com/pypa/virtualenv/1.9.X/virtualenv.py

 Give it execution permission:

    chmod +x virtualenv.py

 Create the virtualenv:

    ./virtualenv.py <env_name> -p <path_to_python>

 Activate:

    source <env_name>/bin/activate

 Python script shebang to use the enviroment:

    '#!<env_name>/bin/python'


## REFERENCES:

<http://www.virtualenv.org/en/latest/>

<http://virtualenvwrapper.readthedocs.org/en/latest/>

<http://virtualenvwrapper.readthedocs.org/en/latest/command_ref.html>

<http://www.cs.dartmouth.edu/~nfoti/blog/blog/2012/07/17/setting-up-virtualenv-
for-data-analysis-on-osx/>
