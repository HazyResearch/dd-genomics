#!/usr/bin/env bash
# A script to start Mindtagger for specific modes
# Author: Jaeho Shin <netj@cs.stanford.edu> / Alex Ratner <ajratner@stanford.edu>
# Created: 2015-01-27
set -eu

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

# Accept options for .conf file and a where clause
shopt -s globstar 2>/dev/null || true
conf=""
where=""
while getopts m:w: opt; do
  case $opt in
  m)
    
    # NOTE: .conf file paths hard-coded here
    case $OPTARG in
    inspect)
      conf="/inspect/..."
      ;;
    precision)
      conf="/precision/..."
      ;;
    recall)
      conf="/recall/..."
    esac
    ;;
  w)
    where=$OPTARG
    ;;
  esac
done
shift $((OPTIND - 1))

# run mindtagger
echo "$conf"
