COPY (
--- WITH relidfeat AS (
---                 SELECT relation_id, unnest(features) as feature FROM gene_hpoterm_relations_is_correct_inference
--- )
SELECT 
     t0.doc_id as doc_id
     , t0.section_id as section_id
     , t0.relation_id  as relation_id 
     , array_to_string(t5.words, '_') || '/' || t6.entity     as relation_name
     , t0.wordidxs_1 as gene_words 
     , t0.wordidxs_2 as hpoterm_words 
     , t1.words       as words
     -- ,  t2.array_accum as sentences_before
     -- ,  t3.array_accum as sentences_after
     ,  t0.expectation as expectation
     --,  t5.expectation as gene_expectation
     --,  t6.expectation as hpoterm_expectation
     --,  t7.features as features
     --,  t7.weights as weights
FROM
        gene_hpoterm_relations_is_correct_inference t0, 
        sentences t1,
-- preceding_sentences t2,
--        following_sentences t3,
        gene_mentions_is_correct_inference t5,
        hpoterm_mentions_is_correct_inference t6
--,
--        ( -- find features relevant to the relation
--        SELECT relation_id
--        , ARRAY_AGG(feature ORDER BY abs(weight) DESC) AS features
--        , ARRAY_AGG(weight ORDER BY abs(weight) DESC) AS weights
--        FROM relidfeat f
--                , dd_inference_result_weights_mapping wm
--        WHERE wm.description = ('classify_gene_hpoterm_relations_features-' || f.feature)
--        GROUP BY relation_id
--        ) t7
WHERE
        t0.doc_id = t1.doc_id AND t0.section_id = t1.section_id AND t0.sent_id_1 = t1.sent_id
AND 
        t0.relation_id not like '%UNSUP'
-- AND 
--         t0.doc_id = t2.doc_id AND t0.sent_id_1 = t2.sent_id
-- AND 
--        t0.doc_id = t3.doc_id AND t0.sent_id_1 = t3.sent_id
-- AND 
--         t0.relation_id = t7.relation_id
AND 
        t0.mention_id_1 = t5.mention_id AND t0.mention_id_2 = t6.mention_id
AND
        t0.expectation < 0.9
AND
        t0.expectation > 0.4
AND
        t0.is_correct is NULL
ORDER BY random()
-- LIMIT 400
LIMIT 500
) TO STDOUT WITH HEADER
;
