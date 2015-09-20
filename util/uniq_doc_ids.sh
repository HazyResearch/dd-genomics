#!/bin/bash -e
set -beEu -o pipefail

#
# Empty the specified table database table
#

if [ $# -ne 1 ]; then
	echo "$0: ERROR: wrong number of arguments" >&2
	echo "$0: USAGE: $0 DB" >&2
	exit 1
fi

DB=$1
START_YEAR=1850
END_YEAR=2015

TMPDIR=$(mktemp -d /tmp/dft.XXXXXX)
SQL_COMMAND_FILE=${TMPDIR}/dft.sql
echo "Uniqing doc ids for >$END_YEAR and <$START_YEAR" > /dev/stderr
cat <<EOF >> ${SQL_COMMAND_FILE}
        DROP TABLE IF EXISTS doc_metadata_uniq;
        CREATE TABLE doc_metadata_uniq AS ( 
          SELECT
            doc_id,
            (array_agg(source_name))[1] as source_name,
            (array_agg(source_year))[1] as source_year,
            (array_agg(source_text_year))[1] as source_text_year,
            (array_agg(source_year_status))[1] as source_year_status,
            (array_agg(issn_global))[1] as issn_global,
            (array_agg(issn_print))[1] as issn_print,
            (array_agg(issn_electronic))[1] as issn_electronic
          FROM 
            doc_metadata
          WHERE source_year < $START_YEAR
          GROUP BY
            doc_id
        );   
EOF
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} || exit 1
rm -rf ${TMPDIR}

for i in $(seq $START_YEAR $END_YEAR)
do
  TMPDIR=$(mktemp -d /tmp/dft.XXXXXX)
  SQL_COMMAND_FILE=${TMPDIR}/dft.sql
  echo "Uniqing doc ids for year $i" > /dev/stderr
  cat <<EOF >> ${SQL_COMMAND_FILE}
        INSERT INTO doc_metadata_uniq ( 
          SELECT
            doc_id,
            (array_agg(source_name))[1] as source_name,
            (array_agg(source_year))[1] as source_year,
            (array_agg(source_text_year))[1] as source_text_year,
            (array_agg(source_year_status))[1] as source_year_status,
            (array_agg(issn_global))[1] as issn_global,
            (array_agg(issn_print))[1] as issn_print,
            (array_agg(issn_electronic))[1] as issn_electronic
          FROM 
            doc_metadata
          WHERE source_year = $i
          GROUP BY
            doc_id
        );   
EOF
  psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} || exit 1
  rm -rf ${TMPDIR}
done

TMPDIR=$(mktemp -d /tmp/dft.XXXXXX)
SQL_COMMAND_FILE=${TMPDIR}/dft.sql
echo "Uniqing doc ids where year is null" > /dev/stderr
cat <<EOF >> ${SQL_COMMAND_FILE}
        INSERT INTO doc_metadata_uniq ( 
          SELECT
            doc_id,
            (array_agg(source_name))[1] as source_name,
            (array_agg(source_year))[1] as source_year,
            (array_agg(source_text_year))[1] as source_text_year,
            (array_agg(source_year_status))[1] as source_year_status,
            (array_agg(issn_global))[1] as issn_global,
            (array_agg(issn_print))[1] as issn_print,
            (array_agg(issn_electronic))[1] as issn_electronic
          FROM 
            doc_metadata
          WHERE source_year is null
          GROUP BY
            doc_id
        );   
        DROP TABLE doc_metadata CASCADE;
        ALTER TABLE doc_metadata_uniq RENAME TO doc_metadata;
EOF
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} || exit 1
rm -rf ${TMPDIR}

psql -U $DBUSER -h $DBHOST -p $DBPORT $DB -X --set ON_ERROR_STOP=1 -c "DROP INDEX IF EXISTS doc_metadata_doc_id;" 
psql -U $DBUSER -h $DBHOST -p $DBPORT $DB -X --set ON_ERROR_STOP=1 -c "CREATE INDEX doc_metadata_doc_id ON doc_metadata (doc_id);"
psql -U $DBUSER -h $DBHOST -p $DBPORT $DB -X --set ON_ERROR_STOP=1 -c "DROP INDEX IF EXISTS doc_metadata_source_year;" 
psql -U $DBUSER -h $DBHOST -p $DBPORT $DB -X --set ON_ERROR_STOP=1 -c "CREATE INDEX doc_metadata_source_year ON doc_metadata (source_year);"

