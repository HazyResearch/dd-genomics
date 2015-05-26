#!/bin/bash -e
set -beEu -o pipefail

if [ "${GDD_HOME-}" == "" ]; then
  echo "Please make sure env_local.sh / env.sh is sourced."
  exit 1
fi

SQL="
CREATE AGGREGATE array_accum(anyelement) (
  SFUNC = array_append,
  STYPE = anyarray,
  INITCOND = '{}'
);

ALTER AGGREGATE public.array_accum(anyelement) OWNER TO ${DBUSER};"

SQL_FILE=`mktemp /tmp/sqlcmd.XXXXX` || exit 1
echo "${SQL}" > ${SQL_FILE}
psql -U ${DBUSER} -h ${DBHOST} -p ${DBPORT} -d ${DBNAME} -f ${SQL_FILE}
