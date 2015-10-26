#! /usr/bin/env bash

${APP_HOME}/util/truncate_table.sh ${DBNAME} genepheno_holdout_set

cat ${APP_HOME}/onto/manual/genepheno_holdout_set.tsv | deepdive sql """COPY genepheno_holdout_set FROM STDIN DELIMITER '	' """

${APP_HOME}/util/uniq_table.sh ${DBNAME} genepheno_holdout_set