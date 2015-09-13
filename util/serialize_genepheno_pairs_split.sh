#!/bin/bash -e
set -beEu -o pipefail

#
# Empty the specified table database table
#

if [ $# -ne 1 ]; then
	echo "$0: ERROR: wrong number of arguments" >&2
	echo "$0: USAGE: $0 DB" >&2
	exit 1
fi

DB=$1
START_YEAR=1850
END_YEAR=2015

TMPDIR=$(mktemp -d /tmp/dft.XXXXXX)
SQL_COMMAND_FILE=${TMPDIR}/dft.sql
echo "Serializing genepheno sentences for >$END_YEAR and <$START_YEAR" > /dev/stderr
cat <<EOF >> ${SQL_COMMAND_FILE}
DROP TABLE IF EXISTS genepheno_pairs_sentences;
CREATE TABLE genepheno_pairs_sentences AS (
  SELECT
    gp.doc_id, 
    gp.section_id, 
    gp.sent_id,
    array_to_string(ARRAY_AGG(gp.gene_mention_id), '|^|') AS gene_mention_ids,
    ARRAY_AGG(gp.gene_name) AS gene_names, 
    array_to_string(ARRAY_AGG(gp.gene_wordidxs), '|^|') AS gene_wordidxs, 
    ARRAY_AGG(gp.gene_is_correct) AS gene_is_corrects, 
    array_to_string(ARRAY_AGG(gp.pheno_mention_id), '|^|') AS pheno_mention_ids,
    ARRAY_AGG(gp.pheno_entity) AS pheno_entities,
    array_to_string(ARRAY_AGG(gp.pheno_wordidxs), '|^|') AS pheno_wordidxs, 
    ARRAY_AGG(gp.pheno_is_correct) AS pheno_is_corrects
  FROM
    genepheno_pairs gp 
    JOIN doc_metadata dm 
      ON (gp.doc_id = dm.doc_id) 
  WHERE
      dm.source_year > $END_YEAR
      OR dm.source_year < $START_YEAR
  GROUP BY
    gp.doc_id, 
    gp.section_id, 
    gp.sent_id
);
EOF
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} || exit 1
rm -rf ${TMPDIR}

for i in $(seq $START_YEAR $END_YEAR)
do
  TMPDIR=$(mktemp -d /tmp/dft.XXXXXX)
  SQL_COMMAND_FILE=${TMPDIR}/dft.sql
  echo "Serializing genepheno sentences for year $i" > /dev/stderr
  cat <<EOF >> ${SQL_COMMAND_FILE}
  INSERT INTO genepheno_pairs_sentences (
    SELECT
      gp.doc_id, 
      gp.section_id, 
      gp.sent_id,
      array_to_string(ARRAY_AGG(gp.gene_mention_id), '|^|') AS gene_mention_ids,
      ARRAY_AGG(gp.gene_name) AS gene_names, 
      array_to_string(ARRAY_AGG(gp.gene_wordidxs), '|^|') AS gene_wordidxs, 
      ARRAY_AGG(gp.gene_is_correct) AS gene_is_corrects, 
      array_to_string(ARRAY_AGG(gp.pheno_mention_id), '|^|') AS pheno_mention_ids,
      ARRAY_AGG(gp.pheno_entity) AS pheno_entities,
      array_to_string(ARRAY_AGG(gp.pheno_wordidxs), '|^|') AS pheno_wordidxs, 
      ARRAY_AGG(gp.pheno_is_correct) AS pheno_is_corrects
    FROM
      genepheno_pairs gp 
      JOIN doc_metadata dm 
        ON (gp.doc_id = dm.doc_id) 
    WHERE
        dm.source_year = $i
    GROUP BY
      gp.doc_id, 
      gp.section_id, 
      gp.sent_id
  );
EOF
  psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} || exit 1
  rm -rf ${TMPDIR}
done

TMPDIR=$(mktemp -d /tmp/dft.XXXXXX)
SQL_COMMAND_FILE=${TMPDIR}/dft.sql
echo "Serializing genepheno sentences where year is null" > /dev/stderr
cat <<EOF >> ${SQL_COMMAND_FILE}
INSERT INTO genepheno_pairs_sentences (
  SELECT
    gp.doc_id, 
    gp.section_id, 
    gp.sent_id,
    array_to_string(ARRAY_AGG(gp.gene_mention_id), '|^|') AS gene_mention_ids,
    ARRAY_AGG(gp.gene_name) AS gene_names, 
    array_to_string(ARRAY_AGG(gp.gene_wordidxs), '|^|') AS gene_wordidxs, 
    ARRAY_AGG(gp.gene_is_correct) AS gene_is_corrects, 
    array_to_string(ARRAY_AGG(gp.pheno_mention_id), '|^|') AS pheno_mention_ids,
    ARRAY_AGG(gp.pheno_entity) AS pheno_entities,
    array_to_string(ARRAY_AGG(gp.pheno_wordidxs), '|^|') AS pheno_wordidxs, 
    ARRAY_AGG(gp.pheno_is_correct) AS pheno_is_corrects
  FROM
    genepheno_pairs gp 
    LEFT OUTER JOIN doc_metadata dm 
      ON (gp.doc_id = dm.doc_id) 
  WHERE
      dm.source_year is null
  GROUP BY
    gp.doc_id, 
    gp.section_id, 
    gp.sent_id
);
EOF
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} || exit 1
rm -rf ${TMPDIR}
