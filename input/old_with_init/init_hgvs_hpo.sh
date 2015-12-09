#! /usr/bin/env bash

${APP_HOME}/util/truncate_table.sh ${DBNAME} hgvs_hpo

cat ${APP_HOME}/onto/data/hgvs_to_hpo.tsv | deepdive sql """COPY hgvs_hpo FROM STDIN DELIMITER '	' """

${APP_HOME}/util/uniq_table.sh ${DBNAME} hgvs_hpo