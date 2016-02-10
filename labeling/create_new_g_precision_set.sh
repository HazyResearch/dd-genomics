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


newdir=OLD/gene-holdout-high-precision-`date +'%Y-%m-%d-%H-%M-%S'`
echo "Moving old genepheno labeling directories to ${newdir}"
mkdir -p OLD
mkdir $newdir
mv *-gene-holdout-high-precision.${NAME} $newdir

echo "Creating new gene-holdout-high-precision Mindtagger task"
./create-new-task.sh gene-holdout-high-precision
for FILENAME in *-gene-holdout-high-precision; do
        mv $FILENAME $FILENAME.$NAME
done
