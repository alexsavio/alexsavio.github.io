#!/bin/bash

# exit if a command returns a non-zero exit code and also print the commands and their args as they are executed
set -e -x

# update the GitLab Runner's packages
apt-get update -yq
apt-get install -yq sudo curl wget ca-certificates

# Download and install required tools.
# pulumi
curl -fsSL https://get.pulumi.com/ | bash
echo "export PATH=$HOME/.pulumi/bin:$PATH" >> ~/.bashrc
export PATH=$HOME/.pulumi/bin:$PATH
# Login into pulumi. This will require the PULUMI_ACCESS_TOKEN environment variable

# Rust
curl https://sh.rustup.rs -sSf | sh -s -- -y
source $HOME/.cargo/env
rustup update

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh
echo "source $HOME/.cargo/env" >> ~/.bashrc
source $HOME/.cargo/env
echo "export PATH=$HOME/.local/bin:$PATH" >> ~/.bashrc
export PATH=$HOME/.local/bin:$PATH

# Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install dependencies
npm ci

# Install Python 3.13
uv python install 3.13

# Just
uv tool install rust-just
