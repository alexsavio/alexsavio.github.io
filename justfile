# Show the version of the blog
version:
  @grep "^VERSION = " pelicanconf.py | cut -d '"' -f 2

# Install the dependencies necessary for CI and development
install:
  uv sync

# Install the dependencies needed for a production installation
install-prod:
  uv sync --no-dev

# Upgrade the dependencies to the latest accepted versions
upgrade:
  uv lock --upgrade

# Audit dependencies for vulnerabilities
audit:
  uv export --no-emit-project --format requirements-txt --output-file requirements.txt
  uv tool run pip-audit --no-deps --disable-pip -r requirements.txt
  rm requirements.txt

##@ Cleanup

# Delete all intermediate files
clean-temp: clean-build clean-pyc clean-pelican

# Delete all intermediate files and caches
clean-all: clean-temp clean-caches

# Delete the Python build files and folders
clean-build:
  rm -fr build/
  rm -fr dist/
  rm -fr *.egg-info
  rm -fr *.spec

# Delete the Python intermediate execution files
clean-pyc:
  find . -name '*~' -exec rm -f {} +
  find . -name '*.log*' -delete
  find . -name '*_cache' -exec rm -rf {} +
  find . -name '*.egg-info' -exec rm -rf {} +
  find . -name '*.pyc' -exec rm -f {} +
  find . -name '*.pyo' -exec rm -f {} +
  find . -name '__pycache__' -exec rm -rf {} +

# Delete Pelican output and cache
clean-pelican:
  rm -rf output/
  rm -rf cache/
  mkdir -p output
  mkdir -p cache

# Delete the test and tool caches
clean-caches:
  rm -rf .coverage
  rm -rf .pytest_cache
  rm -rf .mypy_cache
  rm -rf .ruff_cache

##@ Code check

# Format your code
format:
  uv run ruff format .

# Run mypy check
lint-mypy:
  uv run mypy pelicanconf.py publishconf.py tasks.py

# Run ruff lint check
lint-ruff:
  uv run ruff check --fix .

# Run all code checks
lint: lint-ruff lint-mypy

##@ Pelican tasks

# Build the blog
build:
  uv run pelican -s pelicanconf.py

# Build the blog with delete switch
rebuild:
  uv run pelican -d -s pelicanconf.py

# Build the blog for production
build-prod:
  uv run pelican -s publishconf.py

# Automatically regenerate site upon file modification
regenerate:
  uv run pelican -r -s pelicanconf.py

# Serve the blog at http://localhost:8000/
serve port="8000":
  uv run pelican --listen -s pelicanconf.py -p {{port}}

# Serve the blog on all network interfaces
serve-global port="8000" server="0.0.0.0":
  uv run pelican --listen -s pelicanconf.py -p {{port}} -b {{server}}

# Serve the blog and regenerate on file changes
serve-dev port="8000":
  uv run pelican --listen --autoreload -s pelicanconf.py -p {{port}}

# Build and serve the blog
dev: rebuild serve-dev

# Upload the site via SSH
ssh-upload ssh_host="localhost" ssh_port="22" ssh_user="root" ssh_target="/var/www": publish
  scp -P {{ssh_port}} -r output/* {{ssh_user}}@{{ssh_host}}:{{ssh_target}}

# Upload the site via rsync+ssh
rsync-upload ssh_host="localhost" ssh_port="22" ssh_user="root" ssh_target="/var/www": publish
  rsync -e "ssh -p {{ssh_port}}" -P -rvzc --cvs-exclude --delete output/ {{ssh_user}}@{{ssh_host}}:{{ssh_target}}

# Deploy to GitHub Pages
github-deploy branch="master": publish
  uv run ghp-import -m "Generate Pelican site" -b {{branch}} output
  git push --force origin {{branch}}

##@ Deish the blog (build for production)
publish: build-prod
  @echo "Site built for production in output/"

##@ Development workflow

# Run format, linting, then build
check: format lint build
  @echo "All checks passed!"

# Full development cycle: clean, install, build, and serve
setup: install clean-pelican build serve-dev

# Re-index qmd search (skills + references)
reindex:
  rfx index
  qmd update && qmd embed

# Count files and lines
stats:
  @echo "Files:"
  @find . -name "*.md" -not -path "./.git/*" | wc -l | xargs echo "  Markdown:"
  @echo ""
  @echo "Lines:"
  @find skills -name "SKILL.md" -exec cat {} + | wc -l | xargs echo "  Skills total:"
  @find .claude/skills/references -name "*.md" -exec cat {} + | wc -l | xargs echo "  References total:"

