#!/usr/bin/env bash
# A script to download the latest version of Dashboard, Mindtagger
# Author: Jaeho Shin <netj@cs.stanford.edu>
# Created: 2015-05-27
set -eu

cd "$(dirname "$0")"
PATH="$PWD:$PATH"

# install Mindbender locally if not available or broken
release=${1:-${MINDBENDER_RELEASE:=LATEST}}
tool=./mindbender
mkdir -p "$(dirname "$tool")"
echo >&2 "Downloading Mindbender ($release)..."
curl --location --show-error --output $tool.download \
    https://github.com/netj/mindbender/releases/download/$release/mindbender-$release-$(uname)-$(uname -m).sh
chmod +x $tool.download
mv -f $tool.download $tool

echo "Mindbender was successfully downloaded at $PWD.  You can run it with:"
echo "$PWD/mindbender"
