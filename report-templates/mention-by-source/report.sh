#!/usr/bin/env bash
# Author: Alex Ratner <ajratner@stanford.edu>
#         Jaeho Shin <netj@cs.stanford.edu>
# Refactored: 2015-02-09
# Created: 2015-01-25

# CREATE TABLE doc_source (doc_id TEXT, source TEXT) DISTRIBUTED BY (doc_id);
# COPY doc_source (doc_id, source) FROM '/lfs/local/0/ajratner/Genomics_docid2journal.tsv' DELIMITER '\t';

set -eu

# parameters
: ${table:?name of the table containing the mentions of variable}
: ${column:?name of the column for the variable}


# TODO(alex,jaeho): confirm with new table names!
case $table in
*_mentions)
  m="mention"
  ;;
*_relations)
  m="relation"
  ;;
*)
  error "$table: Unrecognized table name"
esac

# Count mentions by source
run-sql "
    SELECT
      ds.source,
      count(m.*) as total_count,
      count(case when m.${column} then 1 end) as labeled_true,
      count(case when not m.${column} then 1 end) as labeled_false,
      count(case when m.${column} is null and ib.bucket = 0 then 1 end) as bucket_0,
      count(case when m.${column} is null and ib.bucket = 1 then 1 end) as bucket_1,
      count(case when m.${column} is null and ib.bucket = 2 then 1 end) as bucket_2,
      count(case when m.${column} is null and ib.bucket = 3 then 1 end) as bucket_3,
      count(case when m.${column} is null and ib.bucket = 4 then 1 end) as bucket_4,
      count(case when m.${column} is null and ib.bucket = 5 then 1 end) as bucket_5,
      count(case when m.${column} is null and ib.bucket = 6 then 1 end) as bucket_6,
      count(case when m.${column} is null and ib.bucket = 7 then 1 end) as bucket_7,
      count(case when m.${column} is null and ib.bucket = 8 then 1 end) as bucket_8,
      count(case when m.${column} is null and ib.bucket = 9 then 1 end) as bucket_9
    FROM
      ${table} m
    LEFT JOIN
      doc_source ds ON m.doc_id = ds.doc_id
    LEFT JOIN
      ${table}_${column}_inference_bucketed ib ON m.doc_id = ib.doc_id
    WHERE
      m.${m}_id = ib.${m}_id
    GROUP BY
      ds.source
" CSV HEADER >mention-by-source.csv


# Generate human-readable and machine-readable reports
cat >README.md <<EOF
## $table by source

$(html-table-for mention-by-source.csv)
EOF

# TODO transform the CSV into JSON?
cat >report.json <<EOF
{
}
EOF
