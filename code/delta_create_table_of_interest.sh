#! /usr/bin/env bash

psql -X --set ON_ERROR_STOP=1 -U ${DBUSER} -p ${DBPORT} -h ${DBHOST} -c "DROP TABLE IF EXISTS ${2};" ${DBNAME}
psql -X --set ON_ERROR_STOP=1 -U ${DBUSER} -p ${DBPORT} -h ${DBHOST} -c "DROP TABLE IF EXISTS ${3};" ${DBNAME}
psql -X --set ON_ERROR_STOP=1 -U ${DBUSER} -p ${DBPORT} -h ${DBHOST} -f ${APP_HOME}/code/deltaSubsets/${1}/main.sql ${DBNAME}
