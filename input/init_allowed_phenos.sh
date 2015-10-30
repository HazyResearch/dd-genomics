#! /usr/bin/env bash

${APP_HOME}/util/truncate_table.sh ${DBNAME} allowed_phenos

${APP_HOME}/code/create_allowed_phenos_list.py | deepdive sql """COPY allowed_phenos FROM STDIN DELIMITER '	' """

${APP_HOME}/util/uniq_table.sh ${DBNAME} allowed_phenos