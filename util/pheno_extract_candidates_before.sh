#! /bin/sh
# Operations to execute before running the pheno_extract_candidates extractor
${APP_HOME}/util/truncate_table.sh ${DBNAME} pheno_mentions
python ${APP_HOME}/onto/prep_pheno_terms.py
