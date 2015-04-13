#!/usr/bin/env bash
# A script for booting up Mindtagger UI just to inspect some data, in simplest way possible
# Author: Alex Ratner <ajratner@stanford.edu>
# Created: 2015-01-31
set -eu

if [ -f ../env_local.sh ]; then
  echo "Using env_local.sh"
  source ../env_local.sh
else
  echo "Using env.sh"
  source ../env.sh
fi

[[ $# -eq 1 ]] || {
    echo "Usage: $0 SCRIPT_NAME"
    echo " where SCRIPT_NAME is one of:"
    ls configs | sed 's/^/  * /'
    false
}

mode=$1; shift

task=$(date +%Y%m%d)-${mode}
if [[ -e $task ]]; then
    suffix=2
    while [[ -e $task.$suffix ]]; do
        let ++suffix
    done
    task+=.$suffix
fi

trap "rm -rf $task" ERR

# create a folder for the config files and data to run in mindtagger
mkdir $task
cp configs/$mode/input.sql $task/input.sql
cp configs/$mode/mindtagger.conf $task/.
cp configs/$mode/template.html $task/.

# get the data using the sql script
psql -h $DBHOST -p $DBPORT -U $DBUSER $DBNAME \
    <$task/input.sql >$task/input.csv

# set up environment to run Mindtagger
cd "$(dirname "$0")"
PATH="$PWD/../bin:$PATH"

# install Mindbender locally if not available or broken
if ! type mindbender &>/dev/null || ! mindbender version &>/dev/null; then
    release=${MINDBENDER_RELEASE:=LATEST}
    tool=../bin/mindbender
    mkdir -p "$(dirname "$tool")"
    echo >&2 "Downloading Mindbender..."
    curl --location --show-error --output $tool.download \
        https://github.com/netj/mindbender/releases/download/$release/mindbender-$release-$(uname)-$(uname -m).sh
    chmod +x $tool.download
    mv -f $tool.download $tool
fi

# Run mintagger for this single task
shopt -s globstar 2>/dev/null || true
mindbender tagger $task/mindtagger.conf
