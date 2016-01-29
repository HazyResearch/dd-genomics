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
