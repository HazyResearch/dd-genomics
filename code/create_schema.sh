#! /bin/sh
# 
# Create the database tables
# 

SCHEMA_FILE="${GDD_HOME}/code/schema.sql"
if [ ! -r ${SCHEMA_FILE} ]; then
	echo "$0: ERROR: schema file is not readable" >&2
	exit 1
fi

psql -X --set ON_ERROR_STOP=1 -d ${DBNAME} -f ${SCHEMA_FILE} 

