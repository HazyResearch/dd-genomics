COPY (
  SELECT t.doc_id
    , t.section_id
    , t.sent_id
    , t.words
    , t.entity
    , pm.wordidxs
  FROM (
      SELECT si.doc_id AS doc_id
        , si.section_id AS section_id
        , si.sent_id AS sent_id
        , string_to_array(si.words, '|^|') AS words
        , mesh.hpo_id AS entity
      FROM sentences_input si
        , (SELECT * FROM hpo_to_doc_via_mesh ORDER BY random() LIMIT 100) mesh
      WHERE
        si.doc_id = mesh.doc_id) t
    LEFT OUTER JOIN pheno_mentions pm
    ON t.doc_id = pm.doc_id AND t.section_id = pm.section_id AND t.sent_id = pm.sent_id AND t.entity = pm.entity
) TO STDOUT WITH CSV HEADER;
