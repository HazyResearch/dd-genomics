COPY (
  SELECT si.doc_id
    , si.sent_id
    , string_to_array(si.words, '|^|') as words
    , mesh.hpo_id as entity
  FROM sentences_input si, hpo_to_doc_via_mesh mesh
  WHERE si.doc_id = mesh.doc_id
  ORDER BY random() LIMIT 100
) TO STDOUT WITH CSV HEADER;
