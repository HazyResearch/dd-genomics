#!/bin/bash

if [ $# -lt 1 ]; then
        echo "$0: ERROR: wrong number of arguments" >&2
        echo "$0: USAGE: $0 {gene,causation,association} [CONFIDENCE] [OPTOUT]" >&2
	echo "$0: See README for info on options"
        exit 1
fi

. env_local.sh

if [ $# -ge 2 ]; then
	echo "Confidence set to $2"
        CONFIDENCE=$2
fi
if [ $# -eq 3 ] && [ $3 = 'OPTOUT' ]; then
	echo "LOGGING CANCELLED"
        OPTOUT=$3
fi

if [ $1 = 'gene' ]; then
        results_log/compute_gene_stats.sh $CONFIDENCE $OPTOUT
elif [ $1 = 'causation' ]; then
        results_log/compute_causation_stats.sh $CONFIDENCE $OPTOUT
elif [ $1 = 'association' ]; then
	results_log/compute_association_stats.sh $CONFIDENCE $OPTOUT
else
        echo "Argument not valid"
        echo "$0: USAGE: $0 {gene,causation,association} [CONFIDENCE] [OPTOUT]" >&2
        exit 1
fi
