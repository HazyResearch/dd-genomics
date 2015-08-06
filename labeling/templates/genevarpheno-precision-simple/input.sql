COPY (
  SELECT 
    r.relation_id  as relation_id
    , r.genevar_entity as genevar_name
    , r.pheno_entity as pheno_name
    , r.genevar_wordidxs as genevar_wordidxs
    , r.pheno_wordidxs as pheno_wordidxs 
    , string_to_array(si.words, '|^|') as words
  FROM
    genevarpheno_relations r 
    , sentences_input si
  WHERE
    r.doc_id = si.doc_id
    AND r.section_id = si.section_id
    AND r.sent_id = si.sent_id
  ORDER BY random()
  LIMIT 100
) TO STDOUT WITH CSV HEADER;
