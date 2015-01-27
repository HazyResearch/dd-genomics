#!/usr/bin/env bash
set -eu

# default doc_id
[[ $# -gt 0 ]] || set -- journal.pbio.1001475.pdf

# create a list of doc_ids
# TODO which is supposed to be sampled in a rigorous way
ids=
for id; do
    ids+=",''${id//\'/\'\'\'\'}''"
done
ids=${ids#,}

# produce SQL query
echo '
\timing
\set doc_id_to_sample ('"'$ids'"')
'"

COPY (
WITH w AS (
    SELECT doc_id, sent_id, words
      FROM sentences
     WHERE doc_id = :doc_id_to_sample
)
, gm AS (
    SELECT sent_id
         , ARRAY_AGG('{' || ARRAY_TO_STRING(wordidxs, ',') || '}') positions
    FROM (
        SELECT sent_id, wordidxs
          FROM gene_mentions m
             , dd_inference_result_variables mir
         WHERE doc_id = :doc_id_to_sample
           AND m.id = mir.id
    ) m
  GROUP BY sent_id
)
, pm AS (
    SELECT sent_id
         , ARRAY_AGG('{' || ARRAY_TO_STRING(wordidxs, ',') || '}') positions
    FROM (
        SELECT sent_id, wordidxs
          FROM hpoterm_mentions m
             , dd_inference_result_variables mir
         WHERE doc_id = :doc_id_to_sample
           AND m.id = mir.id
    ) m
  GROUP BY sent_id
)

SELECT w.doc_id
     , w.sent_id
     , w.words
     , gm.positions AS g_positions
     , pm.positions AS p_positions
  FROM w
LEFT JOIN gm ON w.sent_id = gm.sent_id
LEFT JOIN pm ON w.sent_id = pm.sent_id

) TO STDOUT WITH CSV HEADER
;

"
