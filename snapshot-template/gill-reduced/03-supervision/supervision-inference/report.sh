#!/usr/bin/env bash
# Common report.sh for data.sql.in-based report templates
# Author: Jaeho Shin <netj@cs.stanford.edu>
# Created: 2015-04-29
set -eu
inputName=data
outputName=data
EXPAND_PARAMETERS=true \
compile-xdocs "$inputName".sql.in
run-sql "$(cat "$inputName".sql)" CSV HEADER | sed 's/f/False/g' | sed 's/t/True/g' | sed 's/associaTrueion/association/g' | sed 's/causaTrueion/causation/g' | sed 's/counTrue/count/g' >"$outputName".csv
json-for "$outputName".csv | transpose-json >"$outputName".json
