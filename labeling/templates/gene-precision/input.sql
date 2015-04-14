COPY (
  SELECT si.doc_id
    , si.sent_id
    , gm.mention_id
    , gm.type
    , string_to_array(si.words, '|^|') as words
    , gm.entity
    , expectation
    , gm.wordidxs
  FROM gene_mentions_is_correct_inference gmi
    , sentences_input si
    , gene_mentions gm
  WHERE si.doc_id = gm.doc_id
    AND si.sent_id = gm.sent_id
    AND gm.mention_id = gmi.mention_id
    AND expectation > 0.9
  ORDER BY random() LIMIT 100
) TO STDOUT WITH CSV HEADER;
