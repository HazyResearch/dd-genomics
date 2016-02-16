#! /bin/bash -e

export NUMERIC=en_US
source env_local.sh
deepdive mark todo genepheno_causation_inferred > /dev/stderr
deepdive redo genepheno_causation_canon > /dev/stderr
deepdive redo allowed_phenos > /dev/stderr
deepdive redo charite > /dev/stderr
deepdive redo charite_canon > /dev/stderr
cd util
./holdout_patch_ddlog.sh
cd ..
redo_weights="n"
echo -n "Redo weights table? [y/n]: "
read redo_weights

echo -n "Number of documents: " 
deepdive sql """ COPY(
select count(distinct doc_id) from sentences_input) TO STDOUT
""" | xargs printf "%'.f\n"
echo -n "Number of documents with body: " 
deepdive sql """ COPY(
select count(distinct doc_id) from sentences_input where section_id like 'Body%') TO STDOUT
""" | xargs printf "%'.f\n"
echo -n "Number of sentences: " 
deepdive sql """ COPY(
select count(*) from sentences_input) TO STDOUT
"""
echo | xargs printf "%'.f\n"

echo -n "Number of gene objects: "
deepdive sql """ COPY(
select count(distinct gene_name) from genes where name_type = 'CANONICAL_SYMBOL') TO STDOUT
""" | xargs printf "%'.f\n"
deepdive sql """ COPY(
select name_type, count(name_type), count(name_type)::float * 100 / (select count(*) from genes) as percentage from genes group by name_type) TO STDOUT
""" | column -t

echo -n "How many gene mention candidates are there in total? "
deepdive sql """ COPY(
select count(*) from (select distinct * from gene_mentions where gene_name is not null) a) TO STDOUT
""" | xargs printf "%'.f\n"

echo -n "How many distinct gene objects do we pick up as candidates? "
deepdive sql """ COPY(
select count(*) from (select distinct g.canonical_name from gene_mentions m join genes g on (m.gene_name = g.gene_name)) a) TO STDOUT
""" | xargs printf "%'.f\n"

echo -n "How many distinct gene objects does Charite contain? "
deepdive sql """ COPY(
select count(*) from (select distinct g.canonical_name from charite c join genes g on c.ensembl_id = g.ensembl_id) a) TO STDOUT
""" | xargs printf "%'.f\n"

echo -n "How many distinct gene objects in Charite that we don't pick up as a candidate? "
deepdive sql """ COPY(
select count(*) from (select distinct c.ensembl_id from charite c left join genes g on c.ensembl_id = g.ensembl_id where g.ensembl_id is null) a) TO STDOUT
""" | xargs printf "%'.f\n"

echo "Breakdown of the gene pickup. WARNING: SQL cannot count NULL values, so random negatives always counted as null:"
deepdive sql """ COPY(
select mapping_type, count(mapping_type), count(mapping_type)::float * 100 / (select count(*) from (select distinct * from gene_mentions) b) as percentage from (select distinct * from gene_mentions) a group by mapping_type) TO STDOUT
""" | column -t

echo -n "How many non-gene-acronym definitions do we pick up? "
deepdive sql """ COPY(
select count(*) from non_gene_acronyms) TO STDOUT
""" | xargs printf "%'.f\n"

echo -n "How many gene mentions do we supervise false as a result of acronym detection? "
deepdive sql """ COPY(
select count(*) from gene_mentions where supertype like '%ABBREV%') TO STDOUT
""" | xargs printf "%'.f\n"
echo

echo -n "How many 'allowed' (non-cancer) HPO phenotypes are there? "
deepdive sql """ COPY(
select count(distinct hpo_id) from allowed_phenos) TO STDOUT
""" | xargs printf "%'.f\n"

echo -n "How many pheno candidates are there in total? "
deepdive sql """ COPY(
select count(*) from (select distinct * from pheno_mentions where entity is not null) a) TO STDOUT
""" | xargs printf "%'.f\n"

echo -n "How many distinct pheno objects do we pick up as candidates? "
deepdive sql """ COPY(
select count(*) from (select distinct entity from pheno_mentions) a) TO STDOUT
""" | xargs printf "%'.f\n"

echo -n "How many distinct phenos are there in Charite (non-canonicalized)? "
deepdive sql """ COPY (
select count(distinct hpo_id) from charite
) TO STDOUT""" | xargs printf "%'.f\n"

echo -n "How many phenos in Charite (non-canonicalized) that we don't even pick up? "
deepdive sql """ COPY(
select count(*) from (select distinct c.hpo_id from charite c left join pheno_mentions pm on (c.hpo_id = pm.entity) where pm.entity is null) a) TO STDOUT
""" | xargs printf "%'.f\n"

echo "Classification of pheno candidates (top 10 classes) (AGAIN WARNING: SQL CANNOT COUNT NULL VALUES):"
deepdive sql """ COPY(
select supertype, count(supertype), count(supertype)::float * 100 / (select count(*) from pheno_mentions) as percentage from pheno_mentions group by supertype order by count desc) TO STDOUT
""" | column -t | head -n 10
echo

echo "How many sentences in which no gene and no pheno candidate occur? "
deepdive sql """
select count(*), count(*)::float * 100 / (select count(*) from sentences_input) AS percentage FROM (
  select distinct si.doc_id, si.section_id, si.sent_id, COALESCE(a.num_gene_candidates, 0) num_gene, COALESCE(b.num_pheno_candidates, 0) num_pheno
  from 
    sentences_input si 
    left join num_gene_candidates a 
      on (si.doc_id = a.doc_id and si.section_id = a.section_id and si.sent_id = a.sent_id)
    left join num_pheno_candidates b 
      on (a.doc_id = b.doc_id and a.section_id = b.section_id and a.sent_id = b.sent_id)
) c
where num_gene = 0 and num_pheno = 0;"""

echo "How many sentences in which at least one gene mention and one pheno mention occur? "
deepdive sql """
select count(*), count(*)::float * 100 / (select count(*) from sentences_input) AS percentage FROM (
  select distinct si.doc_id, si.section_id, si.sent_id, COALESCE(a.num_gene_candidates, 0) num_gene, COALESCE(b.num_pheno_candidates, 0) num_pheno
  from 
    sentences_input si 
    left join num_gene_candidates a 
      on (si.doc_id = a.doc_id and si.section_id = a.section_id and si.sent_id = a.sent_id)
    left join num_pheno_candidates b 
      on (a.doc_id = b.doc_id and a.section_id = b.section_id and a.sent_id = b.sent_id)
) c
where num_gene >= 1 and num_pheno >= 1;"""

echo -n "How many sentences in which at least 2gene mentionss+2pheno mentions occur? "
deepdive sql """
select count(*), count(*)::float * 100 / (select count(*) from sentences_input) AS percentage FROM (
  select distinct si.doc_id, si.section_id, si.sent_id, COALESCE(a.num_gene_candidates, 0) num_gene, COALESCE(b.num_pheno_candidates, 0) num_pheno
  from 
    sentences_input si 
    left join num_gene_candidates a 
      on (si.doc_id = a.doc_id and si.section_id = a.section_id and si.sent_id = a.sent_id)
    left join num_pheno_candidates b 
      on (a.doc_id = b.doc_id and a.section_id = b.section_id and a.sent_id = b.sent_id)
) c
where (num_gene >= 2 and num_pheno >= 2);"""

echo -n "How many gene mention+pheno mention pairs occur in total single sentences (no random negatives)? "
deepdive sql """ COPY(
select count(*) from (select gm.gene_name, pm.entity from genepheno_pairs p join gene_mentions gm on (p.gene_mention_id = gm.mention_id) join pheno_mentions pm on (p.pheno_mention_id = pm.mention_id) where gm.gene_name is not null and pm.entity is not null) a) TO STDOUT
"""

echo -n "How many distinct gene object+pheno pairs occur in total single sentences (no random negatives)? "
deepdive sql """ COPY(
select count(*) from (select distinct canonical_name, pheno_entity from genepheno_pairs p join gene_mentions gm on (p.gene_mention_id = gm.mention_id) join pheno_mentions pm on (p.pheno_mention_id = pm.mention_id) join genes g on (gm.gene_name = g.gene_name) where gm.gene_name is not null and pm.entity is not null) a) TO STDOUT
""" | xargs printf "%'.f\n"

echo -n "How many gene mention+pheno pairs do we subject to inference? (I.e. after all filtering by dependency path distance; after filtering out genes+phenos we CURRENTLY don't like ...) "
deepdive sql """ COPY(
select count(*) from genepheno_causation) TO STDOUT
""" | xargs printf "%'.f\n"

echo "How does the broad gene mention distant supervision picture look? "
deepdive sql """ COPY(
select supertype, count(supertype) from gene_mentions group by supertype order by count desc) TO STDOUT
""" | column -t

echo -n "How does the broad pheno distant supervision picture look? "
echo "TODO, this is currently a mess"

echo "How does the broad genepheno causation supervision picture look? "
deepdive sql """COPY (
select supertype, count(supertype) from genepheno_causation group by supertype order by count desc) TO STDOUT
""" | column -t
echo

if [[ "$redo_weights" -eq "y" ]]
then
  deepdive redo weights > /dev/stderr
  deepdive sql """drop table if exists weights;""" > /dev/stderr
  deepdive sql """create table weights as (select * from dd_inference_result_weights_mapping w) distributed by (id);""" > /dev/stderr
fi

echo -n "How many features do we extract per genepheno causation candidate on average? "
deepdive sql """ COPY(
select a.count::float / b.count::float from (select count(*) as count from genepheno_causation c) b, (select count(*) as count from genepheno_features f join genepheno_causation c on (f.relation_id = c.relation_id)) a) TO STDOUT
"""

echo "What are the highest weighted features for gene mentions? "
deepdive sql """
COPY (
  select description, weight from weights w where w.description like '%gene_mentions_filtered%' order by weight desc limit 10
) TO STDOUT
""" | column -s $'\t' -t
echo

echo "What are the lowest weighted features for gene mentions? "
deepdive sql """
COPY (
  select description, weight from weights w where w.description like '%gene_mentions_filtered%' order by weight asc limit 10
) TO STDOUT
""" | column -s $'\t' -t
echo

echo "What are the highest weighted features for gene-pheno? "
deepdive sql """
COPY (
  select description, weight from weights w where w.description like '%genepheno%' order by weight desc limit 10
) TO STDOUT
""" | column -s $'\t' -t
echo

echo "What are the lowest weighted features for gene-pheno? "
deepdive sql """
COPY (
  select description, weight from weights w where w.description like '%genepheno%' order by weight asc limit 10
) TO STDOUT
""" | column -s $'\t' -t
echo

echo

cd util
echo "Genepheno holdout set stats for causation: "
./gp_holdout_stats_caus.sh
echo

echo "What does the expectation-distribution for gene look like? "
deepdive sql """
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
  COUNT(*) as count,
  COUNT(*)::float * 100 / (select count(*) from gene_mentions_filtered_inference_label_inference) as percentage
FROM gene_mentions_filtered_inference_label_inference
GROUP BY binned_exp
ORDER BY binned_exp
""" | column -t
echo

echo "What does the expectation-distribution for genepheno look like? "
deepdive sql """
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
  COUNT(*),
  COUNT(*)::float * 100 / (select count(*) from genepheno_causation_inference_label_inference) as percentage
FROM genepheno_causation_inference_label_inference
GROUP BY binned_exp
ORDER BY binned_exp
""" | column -t
echo

gp_cutoff=`cat ${GDD_HOME}/results_log/gp_cutoff`

echo -n "How many distinct gene object-pheno causation pairs do we infer with expectation > ${gp_cutoff}? (non-canonicalized pheno) "
deepdive sql """
COPY (
select count(*) from
(select distinct g.canonical_name, c.pheno_entity from genepheno_causation_inference_label_inference i join genepheno_causation c on (i.relation_id = c.relation_id) join genes g on (c.gene_name = g.gene_name) where i.expectation > ${gp_cutoff} )a
) TO STDOUT
""" | xargs printf "%'.f\n"

echo -n "How many distinct gene object-pheno causation pairs do we infer with expectation > ${gp_cutoff}? (canonicalized pheno) "
deepdive sql """
COPY (
select count(*) from (select distinct * from genepheno_causation_canon) a
) TO STDOUT
""" | xargs printf "%'.f\n"

echo -n "How many distinct gene object-pheno pairs does Charite contain (canonicalized phenotypes) with 'allowed' pheno (phenotypic abnormality, non-cancer)? "
deepdive sql """
COPY (
select count(*) from (select distinct c.hpo_id, ensembl_id from charite_canon c join allowed_phenos a on c.hpo_id = a.hpo_id) a
) TO STDOUT
""" | xargs printf "%'.f\n"

echo -n "How many distinct gene objects do we have in genepheno pairs with expectation > ${gp_cutoff}? "
deepdive sql """
COPY (
select count(*) from
(select distinct g.ensembl_id from genepheno_causation_canon g) a
) TO STDOUT
""" | xargs printf "%'.f\n"

echo -n "How many distinct phenos do we have in genepheno pairs with expectation > ${gp_cutoff}? (canonicalized pheno)? "
deepdive sql """
COPY (
select count(*) from
(select distinct hpo_id from genepheno_causation_canon) a
) TO STDOUT
""" | xargs printf "%'.f\n"

echo -n "How many distinct gene object-pheno (canonicalized) pairs do we have inferred that are not in canonicalized Charite? "
deepdive sql """
COPY (
select count(*) from
(select distinct g.ensembl_id, g.hpo_id from genepheno_causation_canon g left join charite_canon cc on (g.ensembl_id = cc.ensembl_id and g.hpo_id = cc.hpo_id) where cc.hpo_id is null) a
) TO STDOUT
""" | xargs printf "%'.f\n"

echo "What are the top journals? I.e. the journals where we inferred most genepheno pairs per document? (Requiring at least 1000 documents in journal)"
deepdive sql """
SELECT
  q1.source_name
  , coalesce(q1.count, 0) as num_docs
  , coalesce(q5.count, 0) as gp_caus_cands
  , to_char(coalesce(q5.count, 0)::float / coalesce((CASE WHEN q1.count = 0 THEN 1 ELSE q1.count END), 1)::float, '999999999D99') as gp_caus_cands_per_doc
  , coalesce(q7.count, 0) as gp_caus_infs
  , to_char(coalesce(q7.count, 0)::float / coalesce((CASE WHEN q1.count = 0 THEN 1 ELSE q1.count END), 1)::float, '999999999D99') as gp_caus_infs_per_doc
  FROM
    (SELECT
      coalesce(source_name, 'UNKNOWN') source_name, count(distinct dm.doc_id)
      FROM
        sentences_input si
        LEFT OUTER JOIN doc_metadata dm ON (si.doc_id = dm.doc_id)
      GROUP BY
        source_name
      HAVING count(distinct dm.doc_id) > 1000
      ORDER BY
        count DESC) q1
    JOIN
    (SELECT
      coalesce(source_name, 'UNKNOWN') source_name, count(distinct dm.doc_id)
      FROM
        genepheno_causation gc
        LEFT OUTER JOIN doc_metadata dm ON (gc.doc_id = dm.doc_id)
      WHERE is_correct != 'f' OR is_correct IS NULL
      GROUP BY
        source_name
      ORDER BY
        count DESC) q5
    ON (q1.source_name = q5.source_name)
    JOIN
    (SELECT
      coalesce(source_name, 'UNKNOWN') source_name, count(distinct dm.doc_id)
      FROM
        genepheno_causation_is_correct_inference gc
        LEFT OUTER JOIN doc_metadata dm ON (gc.doc_id = dm.doc_id)
      WHERE expectation > ${gp_cutoff}
      GROUP BY
        source_name
      ORDER BY
        count DESC) q7
    ON (q5.source_name = q7.source_name)
ORDER BY gp_caus_infs_per_doc DESC
LIMIT 10
"""

echo "What are the top journals? I.e. the journals where we inferred most genepheno pairs per document? (Requiring at least 100 documents in journal)"
deepdive sql """
SELECT
  q1.source_name
  , coalesce(q1.count, 0) as num_docs
  , coalesce(q5.count, 0) as gp_caus_cands
  , to_char(coalesce(q5.count, 0)::float / coalesce((CASE WHEN q1.count = 0 THEN 1 ELSE q1.count END), 1)::float, '999999999D99') as gp_caus_cands_per_doc
  , coalesce(q7.count, 0) as gp_caus_infs
  , to_char(coalesce(q7.count, 0)::float / coalesce((CASE WHEN q1.count = 0 THEN 1 ELSE q1.count END), 1)::float, '999999999D99') as gp_caus_infs_per_doc
  FROM
    (SELECT
      coalesce(source_name, 'UNKNOWN') source_name, count(distinct dm.doc_id)
      FROM
        sentences_input si
        LEFT OUTER JOIN doc_metadata dm ON (si.doc_id = dm.doc_id)
      GROUP BY
        source_name
      HAVING count(distinct dm.doc_id) > 100
      ORDER BY
        count DESC) q1
    JOIN
    (SELECT
      coalesce(source_name, 'UNKNOWN') source_name, count(distinct dm.doc_id)
      FROM
        genepheno_causation gc
        LEFT OUTER JOIN doc_metadata dm ON (gc.doc_id = dm.doc_id)
      WHERE is_correct != 'f' OR is_correct IS NULL
      GROUP BY
        source_name
      ORDER BY
        count DESC) q5
    ON (q1.source_name = q5.source_name)
    JOIN
    (SELECT
      coalesce(source_name, 'UNKNOWN') source_name, count(distinct dm.doc_id)
      FROM
        genepheno_causation_is_correct_inference gc
        LEFT OUTER JOIN doc_metadata dm ON (gc.doc_id = dm.doc_id)
      WHERE expectation > ${gp_cutoff}
      GROUP BY
        source_name
      ORDER BY
        count DESC) q7
    ON (q5.source_name = q7.source_name)
ORDER BY gp_caus_infs_per_doc DESC
LIMIT 10
"""

echo "What are the top allowed phenos in Charite that we didn't pick up?"
deepdive sql """
COPY (
select a.hpo_id, count(a.hpo_id), a.names from charite c join allowed_phenos a on (c.hpo_id = a.hpo_id) left join pheno_mentions p on (p.entity = c.hpo_id) where p.entity is null group by a.hpo_id, a.names order by count desc limit 10
) TO STDOUT
"""
echo

echo "Printing 10 random sentences with genepheno pairs that are inferred true:"
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
    expectation > ${gp_cutoff}
  ) a
group by doc_id, section_id, sent_id, sentence
order by random() limit 10
) TO STDOUT
"""
echo

echo "Printing 10 random sentences with genepheno pairs that are inferred true and are not in Charite:"
deepdive sql """
COPY (
select
  doc_id,
  section_id,
  sent_id,
  ARRAY_AGG(ensembl_id),
  ARRAY_AGG(pheno_entity),
  ARRAY_AGG(gene_name),
  ARRAY_AGG(pheno_word),
  sentence
FROM (
  select distinct
    si.doc_id,
    si.section_id,
    si.sent_id,
    g.ensembl_id,
    gc.pheno_entity,
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
    expectation > ${gp_cutoff}
    and cc.hpo_id is null
  ) a
group by doc_id, section_id, sent_id, sentence
order by random() limit 10
) TO STDOUT
"""
echo

echo "Printing 10 random sentences with gene-disease pairs that are inferred true and not in Charite:"
deepdive sql """
COPY (
SELECT 
  doc_id, 
  section_id, 
  sent_id, 
  ARRAY_AGG(gene_name), 
  ARRAY_AGG(supertype), 
  ARRAY_AGG(pheno_entity), 
  ARRAY_AGG(pheno_name), 
  sentence
FROM (
  select distinct 
    si.doc_id, 
    si.section_id, 
    si.sent_id, 
    gc.gene_name, 
    gc.supertype, 
    gc.pheno_entity, 
    (STRING_TO_ARRAY(pn.names, '|^|'))[1] pheno_name, 
    ARRAY_TO_STRING(STRING_TO_ARRAY(si.words, '|^|'), ' ') sentence 
  from 
    sentences_input si 
    join genepheno_causation gc 
      on (si.doc_id = gc.doc_id and si.section_id = gc.section_id and si.sent_id = gc.sent_id) 
    join genepheno_causation_inference_label_inference i 
      on (gc.relation_id = i.relation_id) 
    join genes g 
      on (g.gene_name = gc.gene_name) 
    join pheno_names pn 
      on (pn.id = gc.pheno_entity) 
    left join charite_disease_canon d 
      on (g.ensembl_id = d.ensembl_id and gc.pheno_entity = d.omim_id) 
  where 
    d.ensembl_id is null 
    and expectation > ${gp_cutoff} 
    and gc.pheno_entity like 'OMIM:%' 
    and pn.names not like '%CANCER%' 
    and pn.names not like '%CARCINOMA%') a 
group by 
  doc_id, section_id, sent_id, sentence 
order by random()
limit 100
) TO STDOUT
"""

echo "Genepheno holdout false positives for causation: "
./gp_holdout_fp_caus_sentences.sh
echo
cd ..

