#!/usr/bin/env bash
# A script for creating new Mindtagger task
# Author: Jaeho Shin <netj@cs.stanford.edu>
# Created: 2015-01-26
set -eu

Here=$(dirname "$0")
cd "$Here"

[[ $# -eq 2 ]] || {
    echo "Usage: $0 NAME MODE"
    echo " where NAME-MODE is one of:"
    ls templates | sed 's/^/  /'
    false
}

Name=$1; shift
Mode=$1; shift

task=$(date +%Y%m%d)-$Name-$Mode
if [[ -e $task ]]; then
    suffix=2
    while [[ -e $task.$suffix ]]; do
        let ++suffix
    done
    task+=.$suffix
fi

# clone a task template
cp -a templates/$Name-$Mode $task

# optionally generate SQL to run for preparing input
if [[ -x $task/input-sql.sh ]]; then
    $task/input-sql.sh "$@" >$task/input.sql
fi

# get input items for the task
psql -h $DBHOST -p $DBPORT -U $DBUSER $DBNAME \
    <$task/input.sql >$task/input.csv
