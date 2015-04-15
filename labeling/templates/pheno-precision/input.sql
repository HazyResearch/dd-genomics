COPY (
  SELECT si.doc_id
    , si.sent_id
    , pm.mention_id
    , pm.type
    , string_to_array(si.words, '|^|') as words
    , pm.entity
    , expectation
    , pm.wordidxs
  FROM pheno_mentions_is_correct_inference pmi
    , sentences_input si
    , pheno_mentions pm
  WHERE si.doc_id = pm.doc_id
    AND si.sent_id = pm.sent_id
    AND pm.mention_id = pmi.mention_id
    AND expectation > 0.9
  ORDER BY random() LIMIT 100
) TO STDOUT WITH CSV HEADER;
