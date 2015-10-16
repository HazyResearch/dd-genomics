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
DROP TABLE IF EXISTS genepheno_holdout_set;
CREATE TABLE genepheno_holdout_set AS (
  SELECT
    doc_id,
    section_id,
    sent_id,
    string_to_array(gene_wordidxs, '|~|')::int[] AS gene_wordidxs,
    string_to_array(pheno_wordidxs, '|~|')::int[] AS pheno_wordidxs
  FROM
    genepheno_pairs gp
  ORDER BY random()
  LIMIT 1000
) DISTRIBUTED BY (doc_id);
EOF
echo "Pulling random 1000 instances from genepheno_pairs"
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} || exit 1
rm -rf ${TMPDIR}

echo "Copying holdout set to onto/manual/genepheno_holdout_set.tsv"
psql -q -X --set ON_ERROR_STOP=1 -d $DB -c 'COPY genepheno_holdout_set TO STDOUT' > ../onto/manual/genepheno_holdout_set.tsv

echo "Creating new genepheno-holdout Mindtagger task"

./create-new-task.sh genepheno-holdout

newdir=OLD/genepheno-holdout-`date +'%Y-%m-%d-%H-%M-%S'`
echo "Moving old labeling directories to OLD/${newdir}"
mkdir $newdir

for i in {AARON,HARENDRA,JOHANNES}
do
  mv *-genepheno-holdout.$i $newdir
done

echo "Tasks for you: "
echo "  * Take the new genepheno-holdout task and create *.{AARON,HARENDRA,JOHANNES} tasks from it"
echo "  * Then (start MindTagger and) create the necessary labels"
echo "  * Don't forget to start and cleanup the backup!"

