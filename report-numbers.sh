#! /bin/bash -e

# deepdive redo allowed_phenos
# deepdive redo charite
# deepdive redo charite_canon
# redo_weights="n"
# echo "Redo weights table? [y/n]"
# read redo_weights
# 
# echo -n "Number of documents: " 
# deepdive sql """ COPY(
# select count(distinct doc_id) from sentences_input) TO STDOUT
# """
# echo
# 
# echo -n "Number of documents with body: " 
# deepdive sql """ COPY(
# select count(distinct doc_id) from sentences_input where section_id like 'Body%') TO STDOUT
# """
# echo 
# 
# echo -n "Number of sentences: " 
# deepdive sql """ COPY(
# select count(*) from sentences_input) TO STDOUT
# """
# echo
# 
# echo -n "Number of gene objects: "
# deepdive sql """ COPY(
# select count(distinct gene_name) from genes where name_type = 'CANONICAL_SYMBOL') TO STDOUT
# """
# echo
# deepdive sql """ COPY(
# select name_type, count(name_type) from genes group by name_type) TO STDOUT
# """ | column -t
# echo
# 
# echo -n "How many gene candidates are there in total? "
# deepdive sql """ COPY(
# select count(*) from (select distinct * from gene_mentions where gene_name is not null) a) TO STDOUT
# """
# echo
# 
# echo -n "How many distinct gene objects do we pick up as candidates? "
# deepdive sql """ COPY(
# select count(*) from (select distinct g.canonical_name from gene_mentions m join genes g on (m.gene_name = g.gene_name)) a) TO STDOUT
# """
# echo
# 
# echo -n "How many distinct gene objects does Charite contain? "
# deepdive sql """ COPY(
# select count(*) from (select distinct g.canonical_name from charite c join genes g on c.ensembl_id = g.ensembl_id) a) TO STDOUT
# """
# echo
# 
# deepdive sql """ COPY(
# select mapping_type, count(mapping_type) from (select distinct * from gene_mentions) a group by mapping_type) TO STDOUT
# """
# echo
# 
# echo -n "How many non-gene-acronym definitions do we pick up? "
# deepdive sql """ COPY(
# select count(*) from non_gene_acronyms) TO STDOUT
# """
# echo
# 
# echo -n "How many genes do we supervise false as a result of acronym detection? "
# deepdive sql """ COPY(
# select count(*) from gene_mentions where supertype like '%ABBREV%') TO STDOUT
# """
# echo 
# 
# echo -n "How many 'allowed' (non-cancer) HPO phenotypes do we have? "
# deepdive sql """ COPY(
# select count(distinct hpo_id) from allowed_phenos) TO STDOUT
# """
# echo
# 
# echo -n "How many synonyms for each pheno on average? "
# echo "TODO"
# echo
# 
# echo -n "How many pheno candidates are there in total? "
# deepdive sql """ COPY(
# select count(*) from (select distinct * from pheno_mentions where entity is not null) a) TO STDOUT
# """
# echo
# 
# echo -n "How many distinct pheno objects do we pick up as candidates? (non-canonicalized, sorry, I'm going to fix this later)"
# deepdive sql """ COPY(
# select count(*) from (select distinct entity from pheno_mentions) a) TO STDOUT
# """
# echo
# 
# echo "Classification of pheno candidates (top 10):"
# deepdive sql """ COPY(
# select supertype, count(supertype) from pheno_mentions group by supertype order by count desc) TO STDOUT
# """ | column -t | head -n 10
# echo
# 
# echo -n "How many distinct pheno objects does charite contain (... also non-canonicalized)? "
# deepdive sql """ COPY(
# select count(distinct hpo_id) from charite) TO STDOUT
# """
# echo
# 
# echo -n "How many gene name+pheno pairs occur in total single sentences (no random negatives)? "
# deepdive sql """ COPY(
# select count(*) from (select gm.gene_name, pm.entity from genepheno_pairs p join gene_mentions gm on (p.gene_mention_id = gm.mention_id) join pheno_mentions pm on (p.pheno_mention_id = pm.mention_id) where gm.gene_name is not null and pm.entity is not null) a) TO STDOUT
# """
# echo
# 
# echo -n "How many distinct gene object+pheno pairs occur in total single sentences (no random negatives)? "
# deepdive sql """ COPY(
# select count(*) from (select distinct canonical_name, pheno_entity from genepheno_pairs p join gene_mentions gm on (p.gene_mention_id = gm.mention_id) join pheno_mentions pm on (p.pheno_mention_id = pm.mention_id) join genes g on (gm.gene_name = g.gene_name) where gm.gene_name is not null and pm.entity is not null) a) TO STDOUT
# """
# echo
# 
# echo -n "How many gene name+pheno pairs do we subject to inference? (I.e. after all filtering by dependency path distance; after filtering out genes+phenos we CURRENTLY don't like ...) "
# deepdive sql """ COPY(
# select count(*) from genepheno_causation) TO STDOUT
# """
# echo
# 
# echo "How does the broad gene distant supervision picture look? "
# deepdive sql """ COPY(
# select supertype, count(supertype) from gene_mentions group by supertype order by count desc) TO STDOUT
# """ | column -t
# echo
# 
# echo -n "How does the broad pheno distant supervision picture look? "
# echo "TODO, this is currently a mess"
# 
# echo "How does the broad genepheno causation supervision picture look? "
# deepdive sql """ COPY(
# select supertype, count(supertype) from genepheno_causation group by supertype order by count desc) TO STDOUT
# """ | column -t
# echo
# 
# echo "... association: TODO"
# echo
# 
# echo -n "How many features do we extract per genepheno causation candidate on average? "
# deepdive sql """ COPY(
# select a.count::float / b.count::float from (select count(*) as count from genepheno_causation c) b, (select count(*) as count from genepheno_features f join genepheno_causation c on (f.relation_id = c.relation_id)) a) TO STDOUT
# """
# echo
# 
# if [[ $redo_weights = "y" ]]
# then
#   deepdive sql """drop table weights;"""
#   deepdive sql """create table weights as (select * from dd_inference_result_weights_mapping w) distributed by (id);"""
# fi
# 
# echo "What are the highest weighted features for gene? "
# deepdive sql """
# COPY (
#   select description, weight from weights w where w.description like '%gene_mentions_filtered%' order by weight desc limit 10
# ) TO STDOUT
# """
# echo
# 
# echo "What are the lowest weighted features for gene? "
# deepdive sql """
# COPY (
#   select description, weight from weights w where w.description like '%gene_mentions_filtered%' order by weight asc limit 10
# ) TO STDOUT
# """ 
# echo
# 
# echo "What are the highest weighted features for gene-pheno? "
# deepdive sql """
# COPY (
#   select description, weight from weights w where w.description like '%genepheno%' order by weight desc limit 10
# ) TO STDOUT
# """
# echo
# 
# echo "What are the lowest weighted features for gene-pheno? "
# deepdive sql """
# COPY (
#   select description, weight from weights w where w.description like '%genepheno%' order by weight asc limit 10
# ) TO STDOUT
# """
# echo
# 
# echo "What does the expectation-distribution for gene look like? "
# deepdive sql """
# COPY (
# SELECT
#   CASE
#     WHEN expectation BETWEEN 0 and 0.1 THEN '0'
#     WHEN expectation BETWEEN 0.1 and 0.2 THEN '0.1'
#     WHEN expectation BETWEEN 0.2 and 0.3 THEN '0.2'
#     WHEN expectation BETWEEN 0.3 and 0.4 THEN '0.3'
#     WHEN expectation BETWEEN 0.4 and 0.5 THEN '0.4'
#     WHEN expectation BETWEEN 0.5 and 0.6 THEN '0.5'
#     WHEN expectation BETWEEN 0.6 and 0.7 THEN '0.6'
#     WHEN expectation BETWEEN 0.7 and 0.8 THEN '0.7'
#     WHEN expectation BETWEEN 0.8 and 0.9 THEN '0.8'
#     WHEN expectation BETWEEN 0.9 and 1 THEN '0.9'
#   END AS binned_exp,
#   COUNT(*)
# FROM gene_mentions_filtered_inference_label_inference
# GROUP BY binned_exp
# ORDER BY binned_exp) TO STDOUT
# """ | column -t
# echo
# 
# echo "What does the expectation-distribution for genepheno look like? "
# deepdive sql """
# COPY (
# SELECT
#   CASE
#     WHEN expectation BETWEEN 0 and 0.1 THEN '0'
#     WHEN expectation BETWEEN 0.1 and 0.2 THEN '0.1'
#     WHEN expectation BETWEEN 0.2 and 0.3 THEN '0.2'
#     WHEN expectation BETWEEN 0.3 and 0.4 THEN '0.3'
#     WHEN expectation BETWEEN 0.4 and 0.5 THEN '0.4'
#     WHEN expectation BETWEEN 0.5 and 0.6 THEN '0.5'
#     WHEN expectation BETWEEN 0.6 and 0.7 THEN '0.6'
#     WHEN expectation BETWEEN 0.7 and 0.8 THEN '0.7'
#     WHEN expectation BETWEEN 0.8 and 0.9 THEN '0.8'
#     WHEN expectation BETWEEN 0.9 and 1 THEN '0.9'
#   END AS binned_exp,
#   COUNT(*)
# FROM genepheno_causation_inference_label_inference
# GROUP BY binned_exp
# ORDER BY binned_exp
# ) TO STDOUT
# """ | column -t
# echo
# 
# echo -n "How many distinct gene object-pheno causation pairs do we infer with expectation > 0.9? "
# deepdive sql """
# COPY (
# select count(*) from
# (select distinct g.canonical_name, c.pheno_entity from genepheno_causation_inference_label_inference i join genepheno_causation c on (i.relation_id = c.relation_id) join genes g on (c.gene_name = g.gene_name) where i.expectation > 0.9 )a
# ) TO STDOUT
# """
# echo
# 
# echo -n "How many distinct gene object-pheno pairs does Charite contain (non-canonicalized phenotypes) with 'allowed' pheno (phenotypic abnormality, non-cancer)? "
# deepdive sql """
# COPY (
# select count(*) from (select distinct c.hpo_id, ensembl_id from charite c join allowed_phenos a on c.hpo_id = a.hpo_id) a
# ) TO STDOUT
# """
# echo
# 
# echo -n "How many distinct gene objects do we have in genepheno pairs with expectation > 0.9? "
# deepdive sql """
# COPY (
# select count(*) from
# (select distinct g.canonical_name from genepheno_causation_inference_label_inference i join genepheno_causation c on (i.relation_id = c.relation_id) join genes g on (c.gene_name = g.gene_name) where i.expectation > 0.9) a
# ) TO STDOUT
# """
# echo

echo -n "How many distinct phenos do we have in genepheno pairs with expectation > 0.9? (non-canonicalized pheno)? "
deepdive sql """
COPY (
select count(*) from
(select distinct pheno_entity from genepheno_causation_inference_label_inference i join genepheno_causation c on (i.relation_id = c.relation_id) join genes g on (c.gene_name = g.gene_name) where i.expectation > 0.9) a
) TO STDOUT
"""
echo

echo -n "How many distinct gene object-pheno pairs do we have inferred that are not in canonicalized Charite? "
deepdive sql """
COPY (
select count(*) from
(select distinct g.canonical_name, pheno_entity from genepheno_causation_inference_label_inference i join genepheno_causation c on (i.relation_id = c.relation_id) join genes g on (c.gene_name = g.gene_name) left join charite_canon cc on (g.ensembl_id = cc.ensembl_id and pheno_entity = cc.hpo_id) where i.expectation > 0.9 and cc.hpo_id is null) a
) TO STDOUT
"""
echo

echo "Printing 20 random sentences with genepheno pairs that are inferred true:"
deepdive sql """
COPY (
select
  doc_id,
  section_id,
  sent_id,
  ARRAY_AGG(gene_name),
  ARRAY_AGG(pheno_word),
  sentence
FROM (
  select distinct
    si.doc_id,
    si.section_id,
    si.sent_id,
    gc.gene_name,
    (STRING_TO_ARRAY(si.words, '|^|'))[gc.pheno_wordidxs[1]+1] pheno_word,
    ARRAY_TO_STRING(STRING_TO_ARRAY(si.words, '|^|'), ' ') sentence
  FROM
    sentences_input si
    join genepheno_causation gc
      on (si.doc_id = gc.doc_id and si.section_id = gc.section_id and si.sent_id = gc.sent_id)
    join genepheno_causation_inference_label_inference i
      on (gc.relation_id = i.relation_id)
    join genes g
      on (gc.gene_name = g.gene_name)
  where
    expectation > 0.9
  ) a
group by doc_id, section_id, sent_id, sentence
order by random() limit 20
) TO STDOUT
"""
echo

echo "Printing 20 random sentences with genepheno pairs that are inferred true and are not in Charite:"
deepdive sql """
COPY (
select
  doc_id,
  section_id,
  sent_id,
  ARRAY_AGG(gene_name),
  ARRAY_AGG(pheno_word),
  sentence
FROM (
  select distinct
    si.doc_id,
    si.section_id,
    si.sent_id,
    gc.gene_name,
    (STRING_TO_ARRAY(si.words, '|^|'))[gc.pheno_wordidxs[1]+1] pheno_word,
    ARRAY_TO_STRING(STRING_TO_ARRAY(si.words, '|^|'), ' ') sentence
  FROM
    sentences_input si
    join genepheno_causation gc
      on (si.doc_id = gc.doc_id and si.section_id = gc.section_id and si.sent_id = gc.sent_id)
    join genepheno_causation_inference_label_inference i
      on (gc.relation_id = i.relation_id)
    join genes g
      on (gc.gene_name = g.gene_name)
    left join charite_canon cc
      on (g.ensembl_id = cc.ensembl_id and gc.pheno_entity = cc.hpo_id)
  where
    expectation > 0.9
    and cc.hpo_id is null
  ) a
group by doc_id, section_id, sent_id, sentence
order by random() limit 20
) TO STDOUT
"""
echo
