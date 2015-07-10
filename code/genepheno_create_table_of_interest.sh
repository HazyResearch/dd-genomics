#! /usr/bin/env bash

psql -X --set ON_ERROR_STOP=1 -U ${DBUSER} -p ${DBPORT} -h ${DBHOST} -c "DROP TABLE IF EXISTS genepheno_old_inferences_of_interest;" ${DBNAME}
psql -X --set ON_ERROR_STOP=1 -U ${DBUSER} -p ${DBPORT} -h ${DBHOST} -c "DROP TABLE IF EXISTS genepheno_new_inferences_of_interest;" ${DBNAME}
psql -X --set ON_ERROR_STOP=1 -U ${DBUSER} -p ${DBPORT} -h ${DBHOST} -f ${APP_HOME}/code/deltaSubsets/genepheno/main.sql ${DBNAME}
