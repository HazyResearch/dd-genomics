#!/usr/bin/env bash
# A script to push to upstream
# Author: Jaeho Shin <netj@cs.stanford.edu>
# Created: 2014-10-13
set -eu

# Determine the branch name to push: either the one given or a generated one
branch=${1:-$(date +$USER-%Y%m%d)}

# Move to the root of the Git repo (See: http://stackoverflow.com/a/14127035)
cd "$(git rev-parse --show-toplevel)"

# First commit all changes
git add .
git add -u .
git commit -a -m "push.sh auto-commit before a git push" || true

# Then push to a new branch
git push https://github.com/ajratner/dd-genomics.git HEAD:$branch ||
    # Otherwise, create a patch that can be emailed
    if read -p "Push to GitHub failed. Do you want generate patch files that can be emailed? "; then
        dir="patches/$branch"
        rm -rf "$dir"
        mkdir -p "$dir"
        git fetch
        git format-patch --output-directory="$dir" FETCH_HEAD
        echo "Now, please email the patches created under: $dir"
    fi
