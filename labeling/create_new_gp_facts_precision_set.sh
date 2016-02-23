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


newdir=OLD/genepheno-facts-precision-`date +'%Y-%m-%d-%H-%M-%S'`
echo "Moving old genepheno labeling directories to ${newdir}"
mkdir -p OLD
mkdir $newdir
mv *-genepheno-facts-precision.${NAME} $newdir

echo "Creating new genepheno-facts-precision Mindtagger task"
./create-new-task.sh genepheno-facts-precision
for FILENAME in *-genepheno-facts-precision; do
        mv $FILENAME $FILENAME.$NAME
done
