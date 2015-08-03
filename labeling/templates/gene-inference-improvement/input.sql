COPY (
  SELECT
    r.sent_id
    , r.mention_id
    , r.type
    , r.words
    , r.entity
    , r.expectation
    , r.wordidxs
    , r.doc_id
    , r.section_id
    , r.diff
  FROM
    gene_inference_delta_improvement r
  ORDER BY random()
  LIMIT 100
) TO STDOUT WITH CSV HEADER;
