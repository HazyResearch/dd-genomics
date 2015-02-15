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
      count(DISTINCT(m.doc_id)) as total_count,
      count(DISTINCT(case when m.is_correct then m.doc_id end)) as labeled_true,
      count(DISTINCT(case when not m.is_correct then m.doc_id end)) as labeled_false,
      count(DISTINCT(case when m.is_correct is null and ib.bucket = 0 then m.doc_id end)) as bucket_0,
      count(DISTINCT(case when m.is_correct is null and ib.bucket = 1 then m.doc_id end)) as bucket_1,
      count(DISTINCT(case when m.is_correct is null and ib.bucket = 2 then m.doc_id end)) as bucket_2,
      count(DISTINCT(case when m.is_correct is null and ib.bucket = 3 then m.doc_id end)) as bucket_3,
      count(DISTINCT(case when m.is_correct is null and ib.bucket = 4 then m.doc_id end)) as bucket_4,
      count(DISTINCT(case when m.is_correct is null and ib.bucket = 5 then m.doc_id end)) as bucket_5,
      count(DISTINCT(case when m.is_correct is null and ib.bucket = 6 then m.doc_id end)) as bucket_6,
      count(DISTINCT(case when m.is_correct is null and ib.bucket = 7 then m.doc_id end)) as bucket_7,
      count(DISTINCT(case when m.is_correct is null and ib.bucket = 8 then m.doc_id end)) as bucket_8,
      count(DISTINCT(case when m.is_correct is null and ib.bucket = 9 then m.doc_id end)) as bucket_9
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
