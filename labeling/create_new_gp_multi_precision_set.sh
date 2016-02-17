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


newdir=OLD/genepheno-multi-precision-`date +'%Y-%m-%d-%H-%M-%S'`
echo "Moving old genepheno labeling directories to ${newdir}"
mkdir -p OLD
mkdir $newdir
mv *-genepheno-multi-precision.${NAME} $newdir

echo "Creating new genepheno-multi-precision Mindtagger task"
./create-new-task.sh genepheno-multi-precision
for FILENAME in *-genepheno-multi-precision; do
        mv $FILENAME $FILENAME.$NAME
done
