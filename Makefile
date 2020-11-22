-include $(shell curl -sSL -o .build-harness "https://git.io/build-harness"; echo .build-harness)

PY?=python3
PELICAN?=pelican
PELICANOPTS=

BASEDIR=$(CURDIR)
INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
CONFFILE=$(BASEDIR)/pelicanconf.py
PUBLISHCONF=$(BASEDIR)/publishconf.py

SSH_HOST=localhost
SSH_PORT=22
SSH_USER=root
SSH_TARGET_DIR=/var/www

GITHUB_PAGES_BRANCH=master

DEBUG ?= 0
ifeq ($(DEBUG), 1)
	PELICANOPTS += -D
endif

RELATIVE ?= 0
ifeq ($(RELATIVE), 1)
	PELICANOPTS += --relative-urls
endif

.PHONY : help
## This help screen
help:
	@printf "Available targets:\n\n"
	@$(SELF) -s help/generate MAKEFILE_LIST="Makefile"

.PHONY: pre-install
pre-install:
	python -m pip install -U pip setuptools pipenv

.PHONY: install
## Install runtime dependencies
install: pre-install
	pipenv install

.PHONY: install-ci
## Install the dependencies for the CI/CD pipeline
install-ci: pre-install
	pipenv install --dev

.PHONY: install-dev
## Install runtime, development dependencies, and pre-commit config
install-dev: install-ci
	pre-commit install

.PHONY: clean
## Clean all temporary build files
clean:: clean-build clean-pyc

.PHONY: clean-build
## Clean the output dir
clean-build:
	[ ! -d $(OUTPUTDIR) ] || rm -rf $(OUTPUTDIR)

.PHONY: clean-pyc
## Clean temporary python files
clean-pyc:
	pyclean .
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '*.log*' -delete
	find . -name '*_cache' -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +

.PHONY: html
## (re)generate the web site
html:
	$(PELICAN) --verbose --debug $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

.PHONY: regenerate
## regenerate files upon modification
regenerate:
	$(PELICAN) -r $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

.PHONY: serve [PORT=8000]
## serve site at http://localhost:8000
serve:
ifdef PORT
	$(PELICAN) -l $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS) -p $(PORT)
else
	$(PELICAN) -l $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)
endif

.PHONY: serve-global
## serve (as root) to $(SERVER):80
serve-global:
ifdef SERVER
	$(PELICAN) -l $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS) -p $(PORT) -b $(SERVER)
else
	$(PELICAN) -l $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS) -p $(PORT) -b 0.0.0.0
endif

.PHONY: devserver
## serve and regenerate together
devserver:
ifdef PORT
	$(PELICAN) -lr $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS) -p $(PORT)
else
	$(PELICAN) -lr $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)
endif

.PHONY: publish
## generate using production settings
publish:
	$(PELICAN) $(INPUTDIR) -o $(OUTPUTDIR) -s $(PUBLISHCONF) $(PELICANOPTS)

.PHONY: ssh_upload
## upload the web site via SSH
ssh_upload: publish
	scp -P $(SSH_PORT) -r $(OUTPUTDIR)/* $(SSH_USER)@$(SSH_HOST):$(SSH_TARGET_DIR)

.PHONY: rsync_upload
## upload the web site via rsync+ssh
rsync_upload: publish
	rsync -e "ssh -p $(SSH_PORT)" -P -rvzc --cvs-exclude --delete $(OUTPUTDIR)/ $(SSH_USER)@$(SSH_HOST):$(SSH_TARGET_DIR)

.PHONY: github
## upload the web site via gh-pages
github: publish
	ghp-import -m "Generate Pelican site" -b $(GITHUB_PAGES_BRANCH) $(OUTPUTDIR)
	git push --force origin $(GITHUB_PAGES_BRANCH)
