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


newdir=OLD/genepheno-holdout-50-75-`date +'%Y-%m-%d-%H-%M-%S'`
echo "Moving old genepheno recall labeling directories to ${newdir}"
mkdir -p OLD
mkdir $newdir
mv *-genepheno-holdout-50-75.${NAME} $newdir

echo "Creating new genepheno-holdout-50-75 Mindtagger task"
./create-new-task.sh genepheno-holdout-50-75
for FILENAME in *-genepheno-holdout-50-75; do
        mv $FILENAME $FILENAME.$NAME
done
