#! /bin/zsh

i=2003
while [[ $i -lt 2014 ]]
do
  echo "Extracting for year $i" > /dev/stderr
  psql -U jbirgmei -h localhost -p 6432 -c "COPY (
  SELECT
    si.doc_id, 
    si.source_name,
    si.mesh_terms,
    CASE WHEN av.pmid IS NULL THEN 0 ELSE 1 END as sv,
    ARRAY_TO_STRING(ARRAY_AGG(si.lemmas), '|~^~|'), 
    ARRAY_TO_STRING(ARRAY_AGG(COALESCE(gm.wordidxs, 'N')), '|~^~|'),
    ARRAY_TO_STRING(ARRAY_AGG(COALESCE(pm.wordidxs, 'N')), '|~^~|') 
  FROM 
    (SELECT si.*, dm.source_name, dm.mesh_terms FROM sentences_input si JOIN doc_metadata dm on (si.doc_id = dm.doc_id) WHERE dm.source_year = $i) si
    LEFT JOIN (
      SELECT DISTINCT 
        doc_id, 
        section_id, 
        sent_id, 
        ARRAY_TO_STRING(ARRAY_AGG(wordidxs[1]), '|^+^|') wordidxs 
      FROM 
        gene_mentions gm
      WHERE
        gm.is_correct = 't' OR gm.is_correct IS NULL
      GROUP BY
        doc_id, 
        section_id, 
        sent_id
    ) gm 
      ON (
        si.doc_id = gm.doc_id AND
        si.section_id = gm.section_id AND
        si.sent_id = gm.sent_id)
    LEFT JOIN (
      SELECT DISTINCT
        doc_id,
        section_id,
        sent_id,
        ARRAY_TO_STRING(ARRAY_AGG(wordidxs[1]), '|^+^|') wordidxs
      FROM 
        pheno_mentions pm
      WHERE
        pm.is_correct = 't' OR pm.is_correct IS NULL
      GROUP BY
        doc_id,
        section_id,
        sent_id
    ) pm
      ON (
        si.doc_id = pm.doc_id AND
        si.section_id = pm.section_id AND
        si.sent_id = pm.sent_id)
    LEFT JOIN omim_allelic_variant_pmids av
      ON (si.doc_id = av.pmid)
  GROUP BY 
    si.doc_id, si.source_name, si.mesh_terms, av.pmid) TO STDOUT" genomics_production_2
  ((i = $i + 1))
done
