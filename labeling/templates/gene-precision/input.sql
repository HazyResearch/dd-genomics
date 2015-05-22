COPY (
  SELECT DISTINCT ON (r,si.doc_id)
     random() as r,
     si.doc_id
    , si.sent_id
    , gm.mention_id
    , gm.type
    , string_to_array(si.words, '|^|') 
    , gm.entity
    , expectation
    , gm.wordidxs
    , features
    , weights
  FROM gene_mentions_is_correct_inference gmi
    , sentences_input si
    , gene_mentions gm
    , ( -- find features relevant to the relation
       SELECT mention_id
            , ARRAY_AGG(feature ORDER BY abs(weight) DESC) AS features
            , ARRAY_AGG(weight  ORDER BY abs(weight) DESC) AS weights
         FROM gene_features f
            , dd_inference_result_weights_mapping wm
        WHERE wm.description = ('gene_inference-' || f.feature)
          AND abs(weight) >= 1
        GROUP BY mention_id
      ) f
  WHERE si.doc_id = gm.doc_id
    AND si.sent_id = gm.sent_id
    AND gm.mention_id = gmi.mention_id
    and gm.mention_id = f.mention_id
    AND expectation > 0.9
  ORDER BY r LIMIT 1000
) TO STDOUT WITH CSV HEADER;
