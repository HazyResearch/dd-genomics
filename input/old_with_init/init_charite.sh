#! /usr/bin/env bash

${APP_HOME}/util/truncate_table.sh ${DBNAME} charite

cat ${APP_HOME}/onto/manual/harendra_phenotype_to_gene.map | deepdive sql """COPY charite FROM STDIN DELIMITER '	' """

${APP_HOME}/util/uniq_table.sh ${DBNAME} charite