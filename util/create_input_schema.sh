#! /bin/sh
# 
# Create the database tables
# 
echo $GDD_HOME
read -r -p "This command will delete any input data (sentences) present- proceed? [y/N] " response
case $response in
	[yY][eE][sS]|[yY]) 
		SCHEMA_FILE="${GDD_HOME}/util/input_schema.sql"
		if [ ! -r ${SCHEMA_FILE} ]; then
			echo "$0: ERROR: schema file is not readable" >&2
			exit 1
		fi
		if [ "$1" == "pg" ]; then
			sed 's@DISTRIBUTED BY .*;@;@g' ${SCHEMA_FILE} | psql -X --set ON_ERROR_STOP=1 -d ${DBNAME} 
		else
			psql -X --set ON_ERROR_STOP=1 -d ${DBNAME} -f ${SCHEMA_FILE} 
		fi
		;;
	*)
		;;
esac
