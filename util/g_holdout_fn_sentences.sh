#!/bin/bash -e
set -beEu -o pipefail

if [ $# -ne 1 ]; then
	echo "$0: ERROR: wrong number of arguments" >&2
	echo "$0: USAGE: $0 DB" >&2
	exit 1
fi

DB=$1

TMPDIR=$(mktemp -d /tmp/dft.XXXXXX)
SQL_COMMAND_FILE=${TMPDIR}/dft.sql
cat <<EOF >> ${SQL_COMMAND_FILE}
COPY (
SELECT DISTINCT
  l.labeler GENE_FALSE_NEGATIVES,
  g.gene_name,
  g.wordidxs,
  array_to_string(string_to_array(si.words, '|^|'), ' ') words
FROM
  gene_mentions_is_correct_inference g
  JOIN gene_holdout_set s 
    ON (s.doc_id = g.doc_id AND s.section_id = g.section_id AND s.sent_id = g.sent_id AND g.wordidxs = s.gene_wordidxs) 
  JOIN genepheno_holdout_labels l
    ON (s.doc_id = l.doc_id AND s.section_id = l.section_id AND s.sent_id = l.sent_id) 
  JOIN sentences_input_with_holdout si
    ON (si.doc_id = l.doc_id AND si.section_id = l.section_id AND si.sent_id = l.sent_id)
WHERE
  g.expectation <= 0.9 
  AND l.is_correct = 't')
TO STDOUT;
EOF
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} > /dev/stderr
rm -rf ${TMPDIR}

