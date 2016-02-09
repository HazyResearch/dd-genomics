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

newdir=OLD/gene-holdout-`date +'%Y-%m-%d-%H-%M-%S'`
echo "Moving old gene labeling directories to ${newdir}"
mkdir -p OLD
mkdir $newdir
mv *-gene-holdout.${NAME} $newdir

echo "Creating new gene-holdout Mindtagger task"
./create-new-task.sh gene-holdout
for FILENAME in *-gene-holdout; do
	mv $FILENAME $FILENAME.$NAME
done
