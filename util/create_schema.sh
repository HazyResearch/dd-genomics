#!/bin/bash -e
set -beEu -o pipefail

# 
# Create the output database tables
# 

if [ "${GDD_HOME-}" == "" ]; then
    echo "Set GDD_HOME to your Genomics DeepDive home directory."
    exit 1
fi
if [ "${DD_DBNAME-${DBNAME-}}" == "" ]; then
    echo "Set DD_DBNAME to your Genomics DeepDive database name."
    exit 1
fi

SCHEMA_FILE="${GDD_HOME}/util/schema.sql"
if [ ! -r ${SCHEMA_FILE} ]; then
    echo "$0: ERROR: schema file is not readable" >&2
    exit 1
fi
sed 's@DISTRIBUTED BY .*;@;@g' ${SCHEMA_FILE} | psql -q -X --set ON_ERROR_STOP=1 -d ${DD_DBNAME-${DBNAME-}}
