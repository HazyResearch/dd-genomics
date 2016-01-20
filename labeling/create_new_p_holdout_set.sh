#!/bin/bash

. ../env_local.sh

if [ $# -eq 1 ]; then
	echo "Setting name to: $1"
	NAME=$1
else
	echo "Setting name to default: $DDNAME"
	NAME=$DDNAME
fi

echo "Name of the labeler $1"
NAME=$1
echo "Extracting holdout from $DBNAME"
DB=$DBNAME

TMPDIR=$(mktemp -d /tmp/dft.XXXXXX)
SQL_COMMAND_FILE=${TMPDIR}/dft.sql
cat <<EOF >> ${SQL_COMMAND_FILE}
DROP TABLE IF EXISTS pheno_holdout_set;
CREATE TABLE pheno_holdout_set AS (
  SELECT
    doc_id,
    section_id,
    sent_id,
    STRING_TO_ARRAY(wordidxs, '|^|')::int[] AS pheno_wordidxs
  FROM
    pheno_mentions_filtered pm
  ORDER BY random()
  LIMIT 1000
) DISTRIBUTED BY (doc_id);
EOF
echo "Pulling random 1000 instances from pheno_mentions"
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} || exit 1
rm -rf ${TMPDIR}

echo "Copying holdout set to onto/manual/pheno_holdout_set.tsv"
psql -q -X --set ON_ERROR_STOP=1 -d $DB -c 'COPY pheno_holdout_set TO STDOUT' > ../onto/manual/pheno_holdout_set.tsv

newdir=OLD/pheno-holdout-`date +'%Y-%m-%d-%H-%M-%S'`
echo "Moving old labeling directories to ${newdir}"
mkdir -p OLD
mkdir $newdir
mv *-pheno-holdout.* $newdir

echo "Creating new pheno-holdout Mindtagger task"
./create-new-task.sh pheno-holdout
for FILENAME in *-pheno-holdout; do
        mv $FILENAME $FILENAME.$NAME
done
