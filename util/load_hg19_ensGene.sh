#! /bin/bash -e
set -beEu -o pipefail

if [ $# -ne 2 ]; then
	echo "$0: ERROR: wrong number of arguments" >&2
	echo "$0: USAGE: $0 DB onto/manual/hg19_ensGenes.sql" >&2
	exit 1
fi

DB=$1

psql -q -X --set ON_ERROR_STOP=1 -d $DB -f $2 || exit 1
