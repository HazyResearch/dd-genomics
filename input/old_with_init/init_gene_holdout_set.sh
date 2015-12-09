#! /usr/bin/env bash

${APP_HOME}/util/truncate_table.sh ${DBNAME} gene_holdout_set

cat ${APP_HOME}/onto/manual/gene_holdout_set.tsv | deepdive sql """COPY gene_holdout_set FROM STDIN DELIMITER '	' """

${APP_HOME}/util/uniq_table.sh ${DBNAME} gene_holdout_set