#!/bin/bash -e
set -beEu -o pipefail

#
# Empty the specified table database table
#

if [ $# -ne 2 ]; then
	echo "$0: ERROR: wrong number of arguments" >&2
	echo "$0: USAGE: $0 DB TABLE" >&2
	exit 1
fi

DB=$1
TABLE=$2
TMPDIR=$(mktemp -d /tmp/dft.XXXXXX)
SQL_COMMAND_FILE=${TMPDIR}/dft.sql

cat <<EOF >> ${SQL_COMMAND_FILE}
TRUNCATE TABLE $TABLE
EOF
psql -X --set ON_ERROR_STOP=1 -d $1 -f ${SQL_COMMAND_FILE} || exit 1

rm -rf ${TMPDIR}

