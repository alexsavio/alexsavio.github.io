Title: Testing Python pipelining modules for a simple neuroimaging task
Date: 2015-08-28 22:15:00
Category: Python
Tags: python, neuroimage, pipeline
Slug: test_python_neuroimaging_pipelining
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: Here I show examples of using different pipeline/workflow definition modules for controlled parallel execution of a simple neuro-imaging task based on a command line.
Status: draft


## Introduction

Current neuroimaging software offer users an incredible opportunity to analyze data using a variety of different algorithms.
However, this has resulted in a heterogeneous collection of specialized applications without transparent interoperability or a uniform operating interface. In addition, the growth of the datasets makes the use of a computer cluster indispensable, which creates the need of task-dependency checks for finer grain parallel task splitting for easier automatization.

I have programmed brain magnetic resonance image (MRI) processing pipelines and tasks in Bash, Matlab, R and Python. Most of them were hard coded, most of the code base is hardly reproducible and not reusable.
In summary, I'm looking for an existing or a good module that allows to define pipelines made of Python functions and command line call tasks and run it in a computer cluster or a multi-core workstation with automatic task-dependency checks. Preferably on Python >= 3.4.

**Note:** *I will be updating this post adding more experiments.*

## Materials

I will use a public available database that I will name [COBRE](http://fcon_1000.projects.nitrc.org/indi/retro/cobre.html).
This database consist of raw anatomical (T1) and functional (fMRI) MR data from 72 patients with Schizophrenia and 75 healthy controls (ages ranging from 18 to 65 in each group). For further reference, I have it downloaded in `~/data/cobre`.

### Method

The experiment I want to try is a non-linear registration using FSL [FLIRT](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT) and [FNIRT](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FNIRT). I want to keep the registration results as well as the linear and non-linear transformation matrices for further processes.

This experiment allows to check important details about the modules under test:
 - task dependency checking,
 - multiple outputs aware,
 - control of the resulting files location.


#### Bash shell

A sequential way to execute this task in shell would be this:

```bash
#!/bin/bash
d=~/data/cobre

in=anat.nii.gz
FNIRT_CFG=${d}/T1_2_MNI152_2mm.cnf

cd $d

lst=`find -name ${in}`
for i in $lst; do
 wd=`dirname $i`
 cd ${wd}
 echo ${wd}

 flirt -ref /usr/share/fsl/4.1/data/standard/MNI152_T1_2mm -in anat -omat anat.to.MNI.mat -out anat_flirted
 fnirt --in=anat.nii --aff=anat.to.MNI.mat --config=${FNIRT_CFG} --cout=anat.to.MNI_field --iout=anat_fnirted
 applywarp --ref=/usr/share/fsl/data/standard/MNI152_T1_2mm --in=anat --warp=anat.to.MNI_field.nii.gz --out=wanat.nii.gz

 cd ${d}

done
```

This is quick, right? But this just provides application specific scalability, and is not easy to port across different architectures.

This could be parallelized using `fsl_sub`, a tool provided by FSL. It is compatible with SGE, PBS and HTCondor. The latter using [patched versions](https://github.com/octomike/fsl_overlay/blob/master/fsl_sub) that take advantage of the HTCondor `qsub` emulation. Given that you have a scheduler set up, enabling `fsl_sub` is as simple as appending `fsl_sub` to the beginning of each task call in the previous code.

The difficulties you will find with parallelizing this in Bash would be:
1. you may need the whole pipeline to be atomic, run one step at a time or add some kind of task-dependency control,
2. the parametrization of the tasks are hardcoded within the pipeline,
3. debugging the pipeline execution will need posterior checking of execution logs,
4. re-using the pipeline for further experiments would require recoding, etc.

Please note that the location of the resulting files is also important for me.


### Selection

I based my search on this list of pipeline modules: https://github.com/pditommaso/awesome-pipeline.

In the next paragraphs I present a list of requirements and desired additions for the modules and a list of the candidates.

#### Requirements
 - Executable in a computer cluster.
 - Automatic task dependency checks.
 - Easy to include/program new tasks.
 - Tasks can do command line calls.
 - Must run the pipelines in more than one open source batch scheduler system, including one of:
    - [HTCondor](https://research.cs.wisc.edu/htcondor/),
    - [Son of Grid Engine](https://arc.liv.ac.uk/trac/SGE),
    - [Open Grid Scheduler](http://gridscheduler.sourceforge.net),
    - [TORQUE](http://www.adaptivecomputing.com/products/open-source/torque/) or
    - [Celery](http://www.celeryproject.org/).

#### Appreciated additions
 - Being usable from Python 3 in GNU/Linux and Mac OS.
 - Workflow graph visualization.
 - Preferred schedulers: [HTCondor](https://research.cs.wisc.edu/htcondor) or [Celery](http://www.celeryproject.org/).
 - Graphical interface for monitoring tasks and nodes.
 - Capacity of resuming the pipeline from an intermediate point, recovering from an error.
 - Compatible with [`drmaa`](http://www.drmaa.org/).

#### Candidates

##### 1. [Nipype](https://github.com/nipy/nipype)

Nipype is **the** neuroimaging pipelining module in Python. It "*provides a uniform interface to existing neuroimaging software and facilitates interaction between these packages within a single workflow*".

According to its website, it allows you to:
- interact with tools from different software packages
- combine processing steps from different software packages
- develop new workflows faster by reusing common steps from old ones
- process data faster by running it in parallel on many cores/machines
- make your research easily reproducible
- share your processing workflows with the community

Nipype is a great module, I have been observing it for a long time. I tried it every time I started a new project, but never got the results how I needed. I used [C-PAC](http://fcp-indi.github.io/) (based on nipype) for processing COBRE, but it is for fMRI only.

+ **Pros:**
 -  Already includes an interface for all the essential neuroimaging tools I need.
 - Very well tested.

I suspect that most of the readers would say: "*Why don't you use nypipe and that's it?!*".
New workflow definition modules are appearing either from companies (Luigi, Airflow) and from other research areas, specially genetic sequency analysis (Ruffus, Cosmos). These modules offer better Workflow definition design API than NiPype, at first sight they seem as powerful, but simpler and less wordy.

##### [Luigi](https://github.com/spotify/luigi)

Luigi is a Python module that helps you build complex pipelines of batch jobs. It handles dependency resolution, workflow management, visualization etc. It also comes with Hadoop support built in.

+ **Pros:**
 -

+ **Cons:**
 -

##### [Ruffus](http://www.ruffus.org.uk/)

##### [Cosmos](https://cosmos.hms.harvard.edu/documentation/index.html)

##### [Airflow](https://github.com/airbnb/airflow)

##### [ActionChain](http://docs.stackstorm.com/actionchain.html)

##### [MakeFlow](http://ccl.cse.nd.edu/software/makeflow/)

##### [NextFlow](http://www.nextflow.io)

##### [SnakeMake](https://bitbucket.org/johanneskoester/snakemake/wiki/browse/)

##### [Common Workflow Language]()

#### Winners


### The implementations

#### Nipype

#### Ruffus

#### Airflow

#### CWL+Ruffus

#### Luigi

#### [Swift](http://swift-lang.org)

#### [CNARI](http://wiki.ci.uchicago.edu/CNARI)

#### [WorldMake](http://worldmake.org)

#### [Taverna](http://www.taverna.org.uk/)

http://stanford.edu/~mwaskom/software/lyman/workflow.html#process-the-data

http://mia.sourceforge.net/

http://fcp-indi.github.io/

### Execution times

## Conclusion

## References
 - https://github.com/pditommaso/awesome-pipeline
 - Gorgolewski K, Burns CD, Madison C, Clark D, Halchenko YO, Waskom ML, Ghosh SS. (2011). Nipype: a flexible, lightweight and extensible neuroimaging data processing framework in Python. Front. Neuroinform. 5:13.
 - https://github.com/nipy/nipype
 - https://github.com/spotify/luigi
 - https://github.com/airbnb/airflow
 - https://cosmos.hms.harvard.edu/documentation/index.html
 - https://bitbucket.org/johanneskoester/snakemake/wiki/browse/
 - https://github.com/pinterest/pinball
 - https://github.com/Illumina/pyflow
 - https://github.com/rabix/rabix
 - https://github.com/soravux/scoop/
 - http://opensource.nibr.com/yap/
 - http://worldmake.org
 - http://www.ruffus.org.uk/
 - https://github.com/common-workflow-language/common-workflow-language/tree/master/reference/
