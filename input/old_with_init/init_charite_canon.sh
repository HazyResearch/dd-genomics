#! /usr/bin/env bash

${APP_HOME}/util/truncate_table.sh ${DBNAME} charite_canon

cat ${APP_HOME}/onto/data/canon_phenotype_to_ensgene.map | deepdive sql """COPY charite_canon FROM STDIN DELIMITER '	' """

${APP_HOME}/util/uniq_table.sh ${DBNAME} charite_canon