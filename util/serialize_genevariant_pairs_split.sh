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
echo "Serializing genevariant sentences for >$END_YEAR and <$START_YEAR" > /dev/stderr
cat <<EOF >> ${SQL_COMMAND_FILE}
DROP TABLE IF EXISTS genevariant_pairs_sentences;
CREATE TABLE genevariant_pairs_sentences AS (
  SELECT
    gv.doc_id, 
    gv.gene_section_id, 
    gv.gene_sent_id,
    gv.variant_section_id, 
    gv.variant_sent_id,
    array_to_string(ARRAY_AGG(gv.gene_mention_id), '|^|') AS gene_mention_ids,
    ARRAY_AGG(gv.gene_name) AS gene_names, 
    array_to_string(ARRAY_AGG(gv.gene_wordidxs), '|^|') AS gene_wordidxs, 
    ARRAY_AGG(gv.gene_is_correct) AS gene_is_corrects, 
    array_to_string(ARRAY_AGG(gv.variant_mention_id), '|^|') AS variant_mention_ids,
    ARRAY_AGG(gv.variant_entity) AS variant_entities,
    array_to_string(ARRAY_AGG(gv.variant_wordidxs), '|^|') AS variant_wordidxs, 
    ARRAY_AGG(gv.variant_is_correct) AS variant_is_corrects
  FROM
    genevariant_pairs gv 
    JOIN doc_metadata dm 
      ON (gv.doc_id = dm.doc_id) 
  WHERE
      dm.source_year > $END_YEAR
      OR dm.source_year < $START_YEAR
  GROUP BY
    gv.doc_id, 
    gv.section_id, 
    gv.sent_id
);
EOF
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} || exit 1
rm -rf ${TMPDIR}

for i in $(seq $START_YEAR $END_YEAR)
do
  TMPDIR=$(mktemp -d /tmp/dft.XXXXXX)
  SQL_COMMAND_FILE=${TMPDIR}/dft.sql
  echo "Serializing genevariant sentences for year $i" > /dev/stderr
  cat <<EOF >> ${SQL_COMMAND_FILE}
  INSERT INTO genevariant_pairs_sentences (
    SELECT
      gv.doc_id, 
      gv.gene_section_id, 
      gv.gene_sent_id,
      gv.variant_section_id, 
      gv.variant_sent_id,
      array_to_string(ARRAY_AGG(gv.gene_mention_id), '|^|') AS gene_mention_ids,
      ARRAY_AGG(gv.gene_name) AS gene_names, 
      array_to_string(ARRAY_AGG(gv.gene_wordidxs), '|^|') AS gene_wordidxs, 
      ARRAY_AGG(gv.gene_is_correct) AS gene_is_corrects, 
      array_to_string(ARRAY_AGG(gv.variant_mention_id), '|^|') AS variant_mention_ids,
      ARRAY_AGG(gv.variant_entity) AS variant_entities,
      array_to_string(ARRAY_AGG(gv.variant_wordidxs), '|^|') AS variant_wordidxs, 
      ARRAY_AGG(gv.variant_is_correct) AS variant_is_corrects
    FROM
      genevariant_pairs gv 
      JOIN doc_metadata dm 
        ON (gv.doc_id = dm.doc_id) 
    WHERE
        dm.source_year = $i
    GROUP BY
      gv.doc_id, 
      gv.section_id, 
      gv.sent_id
  );
EOF
  psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} || exit 1
  rm -rf ${TMPDIR}
done

TMPDIR=$(mktemp -d /tmp/dft.XXXXXX)
SQL_COMMAND_FILE=${TMPDIR}/dft.sql
echo "Serializing genevariant sentences where year is null" > /dev/stderr
cat <<EOF >> ${SQL_COMMAND_FILE}
INSERT INTO genevariant_pairs_sentences (
  SELECT
    gv.doc_id, 
    gv.gene_section_id, 
    gv.gene_sent_id,
    gv.variant_section_id, 
    gv.variant_sent_id,
    array_to_string(ARRAY_AGG(gv.gene_mention_id), '|^|') AS gene_mention_ids,
    ARRAY_AGG(gv.gene_name) AS gene_names, 
    array_to_string(ARRAY_AGG(gv.gene_wordidxs), '|^|') AS gene_wordidxs, 
    ARRAY_AGG(gv.gene_is_correct) AS gene_is_corrects, 
    array_to_string(ARRAY_AGG(gv.variant_mention_id), '|^|') AS variant_mention_ids,
    ARRAY_AGG(gv.variant_entity) AS variant_entities,
    array_to_string(ARRAY_AGG(gv.variant_wordidxs), '|^|') AS variant_wordidxs, 
    ARRAY_AGG(gv.variant_is_correct) AS variant_is_corrects
  FROM
    genevariant_pairs gv 
    LEFT OUTER JOIN doc_metadata dm 
      ON (gv.doc_id = dm.doc_id) 
  WHERE
      dm.source_year is null
  GROUP BY
    gv.doc_id, 
    gv.section_id, 
    gv.sent_id
);
EOF
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} || exit 1
rm -rf ${TMPDIR}
