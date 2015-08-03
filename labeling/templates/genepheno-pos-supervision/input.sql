COPY (
  SELECT 
    r.relation_id  as relation_id
    , r.gene_entity as gene_name
    , r.pheno_entity as pheno_name
    , r.gene_wordidxs as gene_wordidxs
    , r.pheno_wordidxs as pheno_wordidxs 
    , string_to_array(si.words, '|^|') as words
    --, psi.array_accum as sentences_before
    --, fsi.array_accum as sentences_after
    , r.expectation as expectation
    , gm.expectation as gene_expectation
    , pm.expectation as pheno_expectation
    , f.features as features
    , f.weights as weights
  FROM
    genepheno_relations_is_correct_inference r 
    , sentences_input si
    --, preceding_sentences psi
    --, following_sentences fsi
    , gene_mentions_is_correct_inference gm
    , pheno_mentions_is_correct_inference pm
    , ( -- find features relevant to the relation
        SELECT
          relation_id
	  , ARRAY_AGG(feature ORDER BY abs(weight) DESC) AS features
	  , ARRAY_AGG(weight ORDER BY abs(weight) DESC) AS weights
	FROM 
          genepheno_features f
	  , dd_inference_result_weights_mapping wm
	WHERE 
          wm.description = ('genepheno_inference-' || f.feature)
	GROUP BY 
          relation_id
      ) f
  WHERE
    r.doc_id = si.doc_id
    AND r.section_id = si.section_id
    AND r.sent_id = si.sent_id
    AND r.doc_id = gm.doc_id 
    AND r.section_id = gm.section_id
    AND r.doc_id = pm.doc_id
    AND r.section_id = pm.section_id
    AND r.sent_id = gm.sent_id
    AND r.sent_id = pm.sent_id
    AND r.gene_mention_id = gm.mention_id
    AND r.pheno_mention_id = pm.mention_id
    AND r.relation_id = f.relation_id 
    AND r.is_correct IS TRUE
    AND gm.expectation > 0.5
    AND pm.expectation > 0.5
  ORDER BY random()
  LIMIT 100
) TO STDOUT WITH CSV HEADER;
