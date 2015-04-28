#!/bin/bash -e
set -beEu -o pipefail

# 
# Create the database tables
# 

if [ "${GDD_HOME-}" == "" ]; then
    echo "Set GDD_HOME to your Genomics DeepDive home directory."
    exit 1
fi
if [ "${DBNAME-}" == "" ]; then
    echo "Set DBNAME to your Genomics DeepDive database name."
    exit 1
fi

read -r -p "This command will delete any input data (sentences) present- proceed? [y/N] " response
case $response in
    [yY][eE][sS]|[yY]) 
        SCHEMA_FILE="${GDD_HOME}/util/input_schema.sql"
        if [ ! -r ${SCHEMA_FILE} ]; then
            echo "$0: ERROR: schema file is not readable" >&2
            exit 1
        fi
        
        sed 's@DISTRIBUTED BY .*;@;@g' ${SCHEMA_FILE} | psql -q -X --set ON_ERROR_STOP=1 -d ${DBNAME} 
		;;
	*)
		;;
esac
