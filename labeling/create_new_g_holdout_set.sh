#!/bin/bash

if [ $# -ne 1 ]; then
	echo "$0: ERROR: wrong number of arguments" >&2
	echo "$0: USAGE: $0 DB" >&2
	exit 1
fi

DB=$1

TMPDIR=$(mktemp -d /tmp/dft.XXXXXX)
SQL_COMMAND_FILE=${TMPDIR}/dft.sql
cat <<EOF >> ${SQL_COMMAND_FILE}
DROP TABLE IF EXISTS gene_holdout_set;
CREATE TABLE gene_holdout_set AS (
  SELECT
    doc_id,
    section_id,
    sent_id,
    string_to_array(gene_wordidxs, '|~|')::int[] AS gene_wordidxs,
  FROM
    gene_mentions gm
  ORDER BY random()
  LIMIT 1000
) DISTRIBUTED BY (doc_id);
EOF
echo "Pulling random 1000 instances from gene_mentions"
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} || exit 1
rm -rf ${TMPDIR}

echo "Copying holdout set to onto/manual/gene_holdout_set.tsv"
psql -q -X --set ON_ERROR_STOP=1 -d $DB -c 'COPY gene_holdout_set TO STDOUT' > ../onto/manual/gene_holdout_set.tsv

echo "Creating new gene-holdout Mindtagger task"

./create-new-task.sh gene-holdout

newdir=OLD/gene-holdout-`date +'%Y-%m-%d-%H-%M-%S'`
echo "Moving old labeling directories to OLD/${newdir}"
mkdir $newdir

for i in {AARON,HARENDRA,JOHANNES}
do
  mv *-gene-holdout.$i $newdir
done

echo "Tasks for you: "
echo "  * Take the new gene-holdout task and create *.{AARON,HARENDRA,JOHANNES} tasks from it"
echo "  * Then (start MindTagger and) create the necessary labels"
echo "  * Don't forget to start and cleanup the backup!"

