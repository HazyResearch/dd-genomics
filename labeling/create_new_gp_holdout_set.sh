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


newdir=OLD/genepheno-holdout-`date +'%Y-%m-%d-%H-%M-%S'`
echo "Moving old genepheno labeling directories to ${newdir}"
mkdir -p OLD
mkdir $newdir
mv *-genepheno-holdout.${NAME} $newdir

echo "Creating new genepheno-holdout Mindtagger task"
./create-new-task.sh genepheno-holdout
for FILENAME in *-genepheno-holdout; do
        mv $FILENAME $FILENAME.$NAME
done
