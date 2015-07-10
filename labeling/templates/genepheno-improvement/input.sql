COPY (
  SELECT 
    r.relation_id  as relation_id
    , r.type as relation_type
    , r.gene_entity as gene_name
    , r.pheno_entity as pheno_name
    , r.gene_wordidxs as gene_wordidxs
    , r.pheno_wordidxs as pheno_wordidxs 
    , r.words as words
    , r.expectation as expectation
    , r.features as features
    , r.weights as weights
    , r.diff as diff
  FROM
    genepheno_delta_improvement r
  ORDER BY random()
  LIMIT 100
) TO STDOUT WITH CSV HEADER;
