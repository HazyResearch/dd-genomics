#!/bin/bash

if [ $# -lt 2 ]; then
        echo "$0: ERROR: wrong number of arguments" >&2
        echo "$0: USAGE: $0 {gene,causation,association, causation_precision} VERSION [CONFIDENCE] [OPTOUT]" >&2
	echo "$0: See README for info on options"
        exit 1
fi

. env_local.sh
VERSION=$2

if [ $# -ge 3 ]; then
	echo "Confidence set to $3"
        CONFIDENCE=$3
fi
if [ $# -eq 4 ] && [ $4 = 'OPTOUT' ]; then
	echo "LOGGING CANCELLED"
        OPTOUT=$4
fi

if [ $1 = 'gene' ]; then
        results_log/compute_gene_stats.sh $VERSION $CONFIDENCE $OPTOUT
elif [ $1 = 'causation' ]; then
        results_log/compute_causation_stats.sh $VERSION $CONFIDENCE $OPTOUT
elif [ $1 = 'association' ]; then
	results_log/compute_association_stats.sh $VERSION $CONFIDENCE $OPTOUT
elif [ $1 = 'causation_precision' ]; then
        results_log/compute_causation_precision_stats.sh $VERSION $CONFIDENCE $OPTOUT
else
        echo "Argument not valid"
        echo "$0: USAGE: $0 {gene,causation,association,causation_precision} VERSION [CONFIDENCE] [OPTOUT]" >&2
        exit 1
fi
