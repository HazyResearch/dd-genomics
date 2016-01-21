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
DROP TABLE IF EXISTS genepheno_holdout_set;
CREATE TABLE genepheno_holdout_set AS (
  SELECT
    doc_id,
    section_id,
    sent_id,
    string_to_array(gene_wordidxs, '|~|')::int[] AS gene_wordidxs,
    string_to_array(pheno_wordidxs, '|~|')::int[] AS pheno_wordidxs,
    gene_mention_id,
    pheno_mention_id
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

newdir=OLD/genepheno-holdout-`date +'%Y-%m-%d-%H-%M-%S'`
echo "Moving old genepheno labeling directories to ${newdir}"
mkdir -p OLD
mkdir $newdir
mv *-genepheno-holdout.* $newdir

echo "Creating new gene-holdout Mindtagger task"
./create-new-task.sh genepheno-holdout
for FILENAME in *-genepheno-holdout; do
        mv $FILENAME $FILENAME.$NAME
done
