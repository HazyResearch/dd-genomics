COPY (
  SELECT t.doc_id
    , t.sent_id
    , t.words
    , t.entity
    , pm.wordidxs
  FROM (
      SELECT si.doc_id as doc_id
        , si.sent_id as sent_id
        , string_to_array(si.words, '|^|') as words
        , mesh.hpo_id as entity
      FROM sentences_input si
        , (SELECT * FROM hpo_to_doc_via_mesh ORDER BY random() LIMIT 100) mesh
      WHERE
        si.doc_id = mesh.doc_id) t
    LEFT OUTER JOIN pheno_mentions pm
    ON t.doc_id = pm.doc_id AND t.sent_id = pm.sent_id AND t.entity = pm.entity
) TO STDOUT WITH CSV HEADER;
