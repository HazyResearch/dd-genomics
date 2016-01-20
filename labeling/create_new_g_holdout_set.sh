#!/bin/bash

. ../env_local.sh
if [ $# -eq 1 ]; then
        echo "Setting name to: $1"
        NAME=$1
else
        echo "Setting name to default: $DDUSER"
        NAME=$DDUSER
fi
DB=$DBNAME
TMPDIR=$(mktemp -d /tmp/dft.XXXXXX)
SQL_COMMAND_FILE=${TMPDIR}/dft.sql
cat <<EOF >> ${SQL_COMMAND_FILE}
DROP TABLE IF EXISTS gene_holdout_set;
CREATE TABLE gene_holdout_set AS (
  SELECT
    doc_id,
    section_id,
    sent_id,
    STRING_TO_ARRAY(wordidxs, '|^|')::int[] AS gene_wordidxs
  FROM
    gene_mentions_filtered gm
  ORDER BY random()
  LIMIT 1000
) DISTRIBUTED BY (doc_id);
EOF
echo "Pulling random 1000 instances from gene_mentions"
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} || exit 1
rm -rf ${TMPDIR}

echo "Copying holdout set to onto/manual/gene_holdout_set.tsv"
psql -q -X --set ON_ERROR_STOP=1 -d $DB -c 'COPY gene_holdout_set TO STDOUT' > ../onto/manual/gene_holdout_set.tsv

newdir=OLD/gene-holdout-`date +'%Y-%m-%d-%H-%M-%S'`
echo "Moving old gene labeling directories to ${newdir}"
mkdir -p OLD
mkdir $newdir
mv *-gene-holdout.* $newdir

echo "Creating new gene-holdout Mindtagger task"
./create-new-task.sh gene-holdout
for FILENAME in *-gene-holdout; do
	mv $FILENAME $FILENAME.$NAME
done
