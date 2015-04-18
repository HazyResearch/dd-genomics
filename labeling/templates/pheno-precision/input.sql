COPY (
  SELECT si.doc_id
    , si.sent_id
    , pm.mention_id
    , pm.type
    , string_to_array(si.words, '|^|') as words
    , pm.entity
    , expectation
    , pm.wordidxs
    , features
    , weights
  FROM pheno_mentions_is_correct_inference pmi
    , sentences_input si
    , pheno_mentions pm
    , ( -- find features relevant to the relation
       SELECT mention_id
            , ARRAY_AGG(feature ORDER BY abs(weight) DESC) AS features
            , ARRAY_AGG(weight  ORDER BY abs(weight) DESC) AS weights
         FROM pheno_features f
            , dd_inference_result_weights_mapping wm
        WHERE wm.description = ('pheno_inference-' || f.feature)
          AND abs(weight) >= 1
        GROUP BY mention_id
      ) f
  WHERE si.doc_id = pm.doc_id
    AND si.sent_id = pm.sent_id
    AND pm.mention_id = pmi.mention_id
    AND pm.mention_id = f.mention_id
    AND expectation > 0.9
  ORDER BY random() LIMIT 100
) TO STDOUT WITH CSV HEADER;
