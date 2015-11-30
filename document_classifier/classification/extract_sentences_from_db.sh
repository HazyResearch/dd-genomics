#! /bin/zsh

execute_query () {
  query="COPY (
  SELECT
    si.doc_id, 
    si.source_name,
    si.mesh_terms,
    CASE WHEN av.pmid IS NULL THEN 0 ELSE 1 END as sv,
    ARRAY_TO_STRING(ARRAY_AGG(si.lemmas), '|~^~|'), 
    ARRAY_TO_STRING(ARRAY_AGG(COALESCE(gm.wordidxs, 'N')), '|~^~|'),
    ARRAY_TO_STRING(ARRAY_AGG(COALESCE(pm.wordidxs, 'N')), '|~^~|') 
  FROM 
    (SELECT * FROM docs_with_mesh WHERE source_year $1) si
    LEFT JOIN true_gene_mentions gm ON (
        si.doc_id = gm.doc_id AND
        si.section_id = gm.section_id AND
        si.sent_id = gm.sent_id)
    LEFT JOIN true_pheno_mentions pm
      ON (
        si.doc_id = pm.doc_id AND
        si.section_id = pm.section_id AND
        si.sent_id = pm.sent_id)
    LEFT JOIN omim_allelic_variant_pmids av
      ON (si.doc_id = av.pmid)
  GROUP BY 
    si.doc_id, si.source_name, si.mesh_terms, av.pmid) TO STDOUT"
  echo $query >> /dev/stderr
  psql -U jbirgmei -h localhost -p 6432 -c "$query" genomics_production_2
}

# psql -U jbirgmei -h localhost -p 6432 -c "
# DROP TABLE IF EXISTS true_gene_mentions;
# CREATE TABLE true_gene_mentions AS (
#   SELECT DISTINCT
#     doc_id,
#     section_id,
#     sent_id,
#     ARRAY_TO_STRING(ARRAY_AGG(wordidxs[1]), '|^+^|') wordidxs
#   FROM
#     gene_mentions gm
#   WHERE
#     gm.is_correct = 't' OR gm.is_correct IS NULL
#   GROUP BY
#     doc_id,
#     section_id,
#     sent_id
# ) DISTRIBUTED BY (doc_id);
# " genomics_production_2
# 
# psql -U jbirgmei -h localhost -p 6432 -c "
# DROP TABLE IF EXISTS true_pheno_mentions;
# CREATE TABLE true_pheno_mentions AS (
#   SELECT DISTINCT
#     doc_id,
#     section_id,
#     sent_id,
#     ARRAY_TO_STRING(ARRAY_AGG(wordidxs[1]), '|^+^|') wordidxs
#   FROM
#     pheno_mentions pm
#   WHERE
#     pm.is_correct = 't' OR pm.is_correct IS NULL
#   GROUP BY
#     doc_id,
#     section_id,
#     sent_id
# ) DISTRIBUTED BY (doc_id);
# " genomics_production_2
# 
# psql -U jbirgmei -h localhost -p 6432 -c "
# DROP TABLE IF EXISTS docs_with_mesh;
# CREATE TABLE docs_with_mesh AS (
#   SELECT 
#     si.doc_id, 
#     si.section_id, 
#     si.sent_id, 
#     si.lemmas, 
#     dm.source_name, 
#     dm.mesh_terms,
#     dm.source_year
#   FROM
#     sentences_input si 
#     JOIN doc_metadata dm 
#       ON (si.doc_id = dm.doc_id)
# ) DISTRIBUTED BY (doc_id);
# " genomics_production_2

echo "Extracting before year 1970" > /dev/stderr
execute_query " < 1970"

i=1970
while [[ $i -lt 2016 ]]
do
  echo "Extracting for year $i" > /dev/stderr
  execute_query " = $i"
  ((i = $i + 1))
done

echo "Extracting after year 2015 or where year is null" > /dev/stderr
execute_query " > 2015"

# execute_query
