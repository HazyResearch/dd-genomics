#! /usr/bin/env bash

${APP_HOME}/util/truncate_table.sh ${DBNAME} hpo_abnormalities

${APP_HOME}/onto/load_hpo_abnormalities.py | deepdive sql """COPY hpo_abnormalities FROM STDIN DELIMITER '	' """

${APP_HOME}/util/uniq_table.sh ${DBNAME} hpo_abnormalities