#!/bin/bash

if [ $# -lt 1 ]; then
        echo "$0: ERROR: wrong number of arguments" >&2
        echo "$0: Please select a relation to extract gene, pheno or genepheno" >&2
        echo "$0: USAGE: $0 {gene,pheno,genepheno} OPTIONAL_NAME" >&2
        exit 1
fi

source ../env_local.sh

if [ $# -eq 2 ]; then
	echo "Setting name to $2"
	NAME=$2
else
	echo "Setting name to default $DDUSER"
	NAME=$DDUSER
fi

echo "Creating holdout sets"
if [ $1 = 'gene' ]; then
	./create_new_g_holdout_set.sh $NAME
elif [ $1 = 'pheno' ]; then
	./create_new_p_holdout_set.sh $NAME
elif [ $1 = 'genepheno' ]; then
	./create_new_gp_holdout_set.sh $NAME
else 
	echo "Argument not valid"
	echo "$0: USAGE: $0 {gene,pheno,genepheno} OPTIONAL_NAME" >&2
        exit 1
fi

echo "Setting port"
PORT_BASE=8000
N_MINDTAGGER=`ps -e | grep node | wc -l`
export PORT=`expr $N_MINDTAGGER + $PORT_BASE`

echo "Port set to $PORT to avoid collisions"

./start-gui.sh
