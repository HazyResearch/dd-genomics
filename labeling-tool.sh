#!/usr/bin/env bash
# A script to start Mindtagger for tasks under labeling/
# Author: Jaeho Shin <netj@cs.stanford.edu>
# Created: 2014-10-11
set -eu

# set up environment to run Mindtagger
cd "$(dirname "$0")"
PATH="$PWD/bin:$PATH"

# install Mindbender locally if not available or broken
if ! type mindbender &>/dev/null || ! mindbender version &>/dev/null; then
    release=${MINDBENDER_RELEASE:=LATEST}
    tool=bin/mindbender
    mkdir -p bin
    echo >&2 "Downloading Mindbender..."
    curl --location --show-error --output $tool.download \
        https://github.com/netj/mindbender/releases/download/$release/mindbender-$release-$(uname)-$(uname -m).sh
    chmod +x $tool.download
    mv -f $tool.download $tool
fi

# start Mindtagger for all tasks available under labeling/
echo >&2 "Starting Mindtagger for all tasks under labeling/..."
shopt -s globstar 2>/dev/null || true
mindbender tagger labeling/**/mindtagger.conf
