#!/usr/bin/env bash
# Author: Alex Ratner <ajratner@stanford.edu>
# Created: 2015-01-25

set -eu

# TODO(alex): switch to new table names!
case $1 in
gene_mentions)
  m="mention"
  ;;
hpoterm_mentions)
  m="mention"
  ;;
gene_hpoterm_relations)
  m="relation"
  ;;
esac

# Generate the SQL for this task
echo "
  COPY (
    SELECT
      m.entity,
      count(m.*) as total_count,
      count(case when m.is_correct then 1 end) as labeled_true,
      count(case when not m.is_correct then 1 end) as labeled_false,
      count(case when m.is_correct is null and ib.bucket = 0 then 1 end) as bucket_0,
      count(case when m.is_correct is null and ib.bucket = 1 then 1 end) as bucket_1,
      count(case when m.is_correct is null and ib.bucket = 2 then 1 end) as bucket_2,
      count(case when m.is_correct is null and ib.bucket = 3 then 1 end) as bucket_3,
      count(case when m.is_correct is null and ib.bucket = 4 then 1 end) as bucket_4,
      count(case when m.is_correct is null and ib.bucket = 5 then 1 end) as bucket_5,
      count(case when m.is_correct is null and ib.bucket = 6 then 1 end) as bucket_6,
      count(case when m.is_correct is null and ib.bucket = 7 then 1 end) as bucket_7,
      count(case when m.is_correct is null and ib.bucket = 8 then 1 end) as bucket_8,
      count(case when m.is_correct is null and ib.bucket = 9 then 1 end) as bucket_9
    FROM
      ${1} m,
      ${1}_is_correct_inference_bucketed ib
    WHERE
      m.doc_id = ib.doc_id AND
      m.${m}_id = ib.${m}_id
    GROUP BY
      m.entity
  ) TO STDOUT WITH CSV HEADER;
"
