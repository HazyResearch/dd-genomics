#! /usr/bin/env bash

${APP_HOME}/util/truncate_table.sh ${DBNAME} genepheno_holdout_labels

cat ${APP_HOME}/onto/manual/genepheno_holdout_labels.tsv | deepdive sql """COPY genepheno_holdout_labels FROM STDIN DELIMITER '	' """

${APP_HOME}/util/uniq_table.sh ${DBNAME} genepheno_holdout_labels