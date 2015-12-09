#! /usr/bin/env bash

${APP_HOME}/util/truncate_table.sh ${DBNAME} genes

${APP_HOME}/code/load_ensembl_table.sh | deepdive sql """COPY genes FROM STDIN DELIMITER '	' """

${APP_HOME}/util/uniq_table.sh ${DBNAME} genes