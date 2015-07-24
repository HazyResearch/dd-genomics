copy (
select 
  a.relation_id
  , a.supertype as assoc_supertype
  , a.subtype as assoc_subtype
  , c.supertype as cause_supertype
  , c.subtype as cause_subtype
  , a.gene_entity as gene_name
  , a.pheno_entity as pheno_name
  , a.gene_wordidxs as gene_wordidxs
  , a.pheno_wordidxs as pheno_wordidxs
  , string_to_array(si.words, '|^|') as words
  , a.expectation as assoc_expectation
  , c.expectation as cause_expectation
  , gm.expectation as gene_expectation
  , pm.expectation as pheno_expectation
  , f_assoc.features as assoc_features
  , f_assoc.weights as assoc_weights
  , f_cause.features as cause_features
  , f_cause.weights as cause_weights
from
  (select *, 'association' as is_association from genepheno_association_is_correct_inference) a
    join
  (select *, 'causation' as is_causation from genepheno_causation_is_correct_inference) c
    on 
      a.relation_id = c.relation_id
      and a.doc_id = c.doc_id
      and a.sent_id = c.sent_id
      and a.gene_entity = c.gene_entity
      and a.pheno_entity = c.pheno_entity
      and a.gene_wordidxs = c.gene_wordidxs
      and a.pheno_wordidxs = c.pheno_wordidxs
  join
    gene_mentions_is_correct_inference gm
      on 
        a.doc_id = gm.doc_id
        and a.sent_id = gm.sent_id
  join
    pheno_mentions_is_correct_inference pm
      on 
        a.doc_id = pm.doc_id
        and a.sent_id = pm.sent_id
  join
    sentences_input si
      on
        si.doc_id = a.doc_id
        and si.sent_id = a.sent_id
  join
    (SELECT
      relation_id
      , ARRAY_AGG(feature ORDER BY abs(weight) DESC) AS features
      , ARRAY_AGG(weight ORDER BY abs(weight) DESC) AS weights
    FROM 
      genepheno_features f
      , dd_inference_result_weights_mapping wm
    WHERE 
      wm.description = ('genepheno_association_inference-' || f.feature)
    GROUP BY  
      relation_id
    ) f_assoc
      on
        f_assoc.relation_id = a.relation_id
  join
    (SELECT
      relation_id
      , ARRAY_AGG(feature ORDER BY abs(weight) DESC) AS features
      , ARRAY_AGG(weight ORDER BY abs(weight) DESC) AS weights
    FROM 
      genepheno_features f
      , dd_inference_result_weights_mapping wm
    WHERE 
      wm.description = ('genepheno_causation_inference-' || f.feature)
    GROUP BY  
      relation_id
    ) f_cause
      on
        f_cause.relation_id = c.relation_id
where
  a.expectation > 0.9 OR c.expectation > 0.9
order by random()
limit 100)
to stdout with csv header;
