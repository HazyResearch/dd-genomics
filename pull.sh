#!/usr/bin/env bash
# A script to pull upstream changes
# Author: Jaeho Shin <netj@cs.stanford.edu>
# Created: 2014-10-13
set -eu

# Move to the root of the Git repo (See: http://stackoverflow.com/a/14127035)
cd "$(git rev-parse --show-toplevel)"

# First commit all changes
git add .
git add -u .
git commit -a -m "pull.sh auto-commit before a git pull" || true

# Then pull merging recursively preferring the changes made on our side (to avoid all conflicts)
git pull --strategy=recursive -Xours \
    https://github.com/rionda/dd-genomics.git master
