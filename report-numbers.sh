#! /bin/bash -e

deepdive redo allowed_phenos
deepdive redo charite
deepdive redo charite_canon

echo "Number of documents: " 
deepdive sql """ COPY(
select count(distinct doc_id) from sentences_input) TO STDOUT
"""

echo "Number of documents with body: " 
deepdive sql """ COPY(
select count(distinct doc_id) from sentences_input where section_id like 'Body%') TO STDOUT
"""

echo "Number of sentences: " 
deepdive sql """ COPY(
select count(*) from sentences_input) TO STDOUT
"""

echo "Number of gene objects: "
deepdive sql """ COPY(
select count(distinct gene_name) from genes where name_type = 'CANONICAL_SYMBOL') TO STDOUT
"""

deepdive sql """ COPY(
select name_type, count(name_type) from genes group by name_type) TO STDOUT
""" | column -t

echo "How many gene candidates are there in total?"
deepdive sql """ COPY(
select count(*) from (select distinct * from gene_mentions where gene_name is not null) a) TO STDOUT
"""

echo "How many distinct gene objects do we pick up as candidates?"
deepdive sql """ COPY(
select count(*) from (select distinct g.canonical_name from gene_mentions m join genes g on (m.gene_name = g.gene_name)) a) TO STDOUT
"""

echo "How many distinct gene objects does Charite contain?"
deepdive sql """ COPY(
select count(*) from (select distinct g.canonical_name from charite c join genes g on c.ensembl_id = g.ensembl_id) a) TO STDOUT
"""

deepdive sql """ COPY(
select mapping_type, count(mapping_type) from (select distinct * from gene_mentions) a group by mapping_type) TO STDOUT
"""

echo "How many non-gene-acronym definitions do we pick up?"
deepdive sql """ COPY(
select count(*) from non_gene_acronyms) TO STDOUT
"""

echo "How many genes do we supervise false as a result of acronym detection?"
deepdive sql """ COPY(
select count(*) from gene_mentions where supertype like '%ABBREV%') TO STDOUT
"""

echo "How many 'allowed' (non-cancer) HPO phenotypes do we have?"
deepdive sql """ COPY(
select count(distinct hpo_id) from allowed_phenos) TO STDOUT
"""

echo "How many synonyms for each pheno on average?"
echo "TODO"

echo "How many pheno candidates are there in total?"
deepdive sql """ COPY(
select count(*) from (select distinct * from pheno_mentions where entity is not null) a) TO STDOUT
"""

echo "How many distinct pheno objects do we pick up as candidates? (non-canonicalized, sorry, I'm going to fix this later)"
deepdive sql """ COPY(
select count(*) from (select distinct entity from pheno_mentions) a) TO STDOUT
"""

echo "Classification of pheno candidates (top 10):"
deepdive sql """ COPY(
select supertype, count(supertype) from pheno_mentions group by supertype order by count desc) TO STDOUT
""" | column -t | head -n 10

echo "How many distinct pheno objects does charite contain (... also non-canonicalized)?"
deepdive sql """ COPY(
select count(distinct hpo_id) from charite) TO STDOUT
"""

echo "How many gene name+pheno pairs occur in total single sentences (no random negatives)?"
deepdive sql """ COPY(
select count(*) from (select gm.gene_name, pm.entity from genepheno_pairs p join gene_mentions gm on (p.gene_mention_id = gm.mention_id) join pheno_mentions pm on (p.pheno_mention_id = pm.mention_id) where gm.gene_name is not null and pm.entity is not null) a) TO STDOUT
"""

echo "How many distinct gene object+pheno pairs occur in total single sentences (no random negatives)?"
deepdive sql """ COPY(
select count(*) from (select distinct canonical_name, pheno_entity from genepheno_pairs p join gene_mentions gm on (p.gene_mention_id = gm.mention_id) join pheno_mentions pm on (p.pheno_mention_id = pm.mention_id) join genes g on (gm.gene_name = g.gene_name) where gm.gene_name is not null and pm.entity is not null) a) TO STDOUT
"""

echo "How many gene name+pheno pairs do we subject to inference? (I.e. after all filtering by dependency path distance; after filtering out genes+phenos we CURRENTLY don't like ...)"
deepdive sql """ COPY(
select count(*) from genepheno_causation) TO STDOUT
"""

echo "How does the broad gene distant supervision picture look?"
deepdive sql """ COPY(
select supertype, count(supertype) from gene_mentions group by supertype order by count desc) TO STDOUT
""" | column -t

echo "How does the broad pheno distant supervision picture look?"
echo "TODO, this is currently a mess"

echo "How does the broad genepheno causation supervision picture look?"
deepdive sql """ COPY(
select supertype, count(supertype) from genepheno_causation group by supertype order by count desc) TO STDOUT
""" | column -t

echo "... association: TODO"

echo "How many features do we extract per genepheno causation candidate on average?"
deepdive sql """ COPY(
select a.count::float / b.count::float from (select count(*) as count from genepheno_causation c) b, (select count(*) as count from genepheno_features f join genepheno_causation c on (f.relation_id = c.relation_id)) a) TO STDOUT
"""

deepdive sql """drop table weights;"""
deepdive sql """create table weights as (select * from dd_inference_result_weights_mapping w) distributed by (id);"""

echo "What are the highest weighted features for gene?"
deepdive sql """
COPY (
  select description, weight from weights w where w.description like '%gene_mentions_filtered%' order by weight desc limit 10
) TO STDOUT
"""

echo "What are the lowest weighted features for gene?"
deepdive sql """
COPY (
  select description, weight from weights w where w.description like '%gene_mentions_filtered%' order by weight asc limit 10
) TO STDOUT
"""

echo "What are the highest weighted features for gene-pheno?"
deepdive sql """
COPY (
  select description, weight from weights w where w.description like '%genepheno%' order by weight desc limit 10
) TO STDOUT
"""

echo "What are the lowest weighted features for gene-pheno?"
deepdive sql """
COPY (
  select description, weight from weights w where w.description like '%genepheno%' order by weight asc limit 10
) TO STDOUT
"""

echo "What does the expectation-distribution for gene look like?"
deepdive sql """
COPY (
SELECT
  CASE
    WHEN expectation BETWEEN 0 and 0.1 THEN '0'
    WHEN expectation BETWEEN 0.1 and 0.2 THEN '0.1'
    WHEN expectation BETWEEN 0.2 and 0.3 THEN '0.2'
    WHEN expectation BETWEEN 0.3 and 0.4 THEN '0.3'
    WHEN expectation BETWEEN 0.4 and 0.5 THEN '0.4'
    WHEN expectation BETWEEN 0.5 and 0.6 THEN '0.5'
    WHEN expectation BETWEEN 0.6 and 0.7 THEN '0.6'
    WHEN expectation BETWEEN 0.7 and 0.8 THEN '0.7'
    WHEN expectation BETWEEN 0.8 and 0.9 THEN '0.8'
    WHEN expectation BETWEEN 0.9 and 1 THEN '0.9'
  END AS binned_exp,
  COUNT(*)
FROM gene_mentions_filtered_inference_label_inference
GROUP BY binned_exp
ORDER BY binned_exp) TO STDOUT
""" | column -t

echo "What does the expectation-distribution for genepheno look like?"
deepdive sql """
COPY (
SELECT
  CASE
    WHEN expectation BETWEEN 0 and 0.1 THEN '0'
    WHEN expectation BETWEEN 0.1 and 0.2 THEN '0.1'
    WHEN expectation BETWEEN 0.2 and 0.3 THEN '0.2'
    WHEN expectation BETWEEN 0.3 and 0.4 THEN '0.3'
    WHEN expectation BETWEEN 0.4 and 0.5 THEN '0.4'
    WHEN expectation BETWEEN 0.5 and 0.6 THEN '0.5'
    WHEN expectation BETWEEN 0.6 and 0.7 THEN '0.6'
    WHEN expectation BETWEEN 0.7 and 0.8 THEN '0.7'
    WHEN expectation BETWEEN 0.8 and 0.9 THEN '0.8'
    WHEN expectation BETWEEN 0.9 and 1 THEN '0.9'
  END AS binned_exp,
  COUNT(*)
FROM genepheno_causation_inference_label_inference
GROUP BY binned_exp
ORDER BY binned_exp;
) TO STDOUT
"""

echo "How many distinct gene object-pheno causation pairs do we infer with expectation > 0.9?"
deepdive sql """
COPY (
select count(*) from
(select distinct g.canonical_name, c.pheno_entity from genepheno_causation_inference_label_inference i join genepheno_causation c on (i.relation_id = c.relation_id) join genes g on (c.gene_name = g.gene_name) a
) TO STDOUT
"""

echo "How many distinct gene object-pheno pairs does Charite contain
(non-canonicalized phenotypes) with 'allowed' pheno (phenotypic abnormality,
non-cancer)?"
deepdive sql """
COPY (
select count(*) from (select distinct hpo_id, ensembl_id from charite c join allowed_phenos a on c.ensembl_id = a.ensembl_id) a
) TO STDOUT
"""

echo "How many distinct gene objects do we have in genepheno pairs with expectation > 0.9?"
deepdive sql """
COPY (
select count(*) from
(select distinct g.canonical_name from genepheno_causation_inference_label_inference i join genepheno_causation c on (i.relation_id = c.relation_id) join genes g on (c.gene_name = g.gene_name) a
) TO STDOUT
"""

echo "How many distinct phenos do we have in genepheno pairs with expectation > 0.9? (non-canonicalized pheno)?"
deepdive sql """
COPY (
select count(*) from
(select distinct pheno_entity from genepheno_causation_inference_label_inference i join genepheno_causation c on (i.relation_id = c.relation_id) join genes g on (c.gene_name = g.gene_name) a
) TO STDOUT
"""

echo "How many distinct gene object-pheno pairs do we have that are not in canonicalized Charite?"
deepdive sql """
COPY (
select count(*) from
(select distinct g.canonical_name, pheno_entity from genepheno_causation_inference_label_inference i join genepheno_causation c on (i.relation_id = c.relation_id) join genes g on (c.gene_name = g.gene_name) where (pheno_entity, g.ensembl_id) not in (select distinct hpo_id, ensembl_id from charite_canon)) a
) TO STDOUT
"""

echo "Printing 20 random sentences with genepheno pairs that are inferred true:"

echo "Printing 20 random sentences with genepheno pairs that are inferred true and are not in Charite:"
