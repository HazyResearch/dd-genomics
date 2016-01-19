#!/bin/bash -e

#Here we assume that the ddlog database is accessible by "deepdive sql" so correctly defined in db.url

cd ..
deepdive sql """DROP VIEW IF EXISTS gene_mentions_filtered_is_correct_inference CASCADE;
CREATE VIEW gene_mentions_filtered_is_correct_inference AS SELECT
g.*,
ginf.category as category, 
ginf.expectation as expectation
from gene_mentions_filtered g,
gene_mentions_filtered_inference_label_inference ginf
where ginf.mention_id = g.mention_id;"""

deepdive sql """DROP VIEW IF EXISTS genepheno_causation_is_correct_inference CASCADE;
CREATE VIEW genepheno_causation_is_correct_inference AS SELECT
g.*,
ginf.category as category, 
ginf.expectation as expectation
from genepheno_causation g,
genepheno_causation_inference_label_inference ginf
where ginf.relation_id = g.relation_id;"""

deepdive sql """DROP VIEW IF EXISTS genepheno_association_is_correct_inference CASCADE;
CREATE VIEW genepheno_association_is_correct_inference AS SELECT
g.*,
ginf.category as category, 
ginf.expectation as expectation
from genepheno_association g,
genepheno_association_inference_label_inference ginf
where ginf.relation_id = g.relation_id;"""

deepdive sql """
DELETE FROM gene_holdout_set 
WHERE (doc_id, section_id, sent_id, gene_wordidxs) IN 
(SELECT DISTINCT
  s.* 
FROM
  gene_holdout_set s 
  LEFT JOIN 
  gene_mentions_filtered p
    ON (s.doc_id = p.doc_id AND s.section_id = p.section_id AND s.sent_id = p.sent_id AND s.gene_wordidxs = STRING_TO_ARRAY(p.wordidxs, '|~|')::INTEGER[]) WHERE p.doc_id IS NULL);

DELETE FROM gene_holdout_labels WHERE (doc_id, section_id, sent_id) NOT IN (SELECT DISTINCT doc_id, section_id, sent_id FROM gene_holdout_set);

DROP TABLE IF EXISTS sentences_input_with_holdout_g;
CREATE TABLE sentences_input_with_holdout_g AS (
  SELECT si.*
  FROM 
    sentences_input_with_gene_mention si
    JOIN gene_holdout_set s
      ON (si.doc_id = s.doc_id)
) DISTRIBUTED BY (doc_id);
"""

deepdive sql """
DELETE FROM genepheno_holdout_set 
WHERE (doc_id, section_id, sent_id, gene_wordidxs, pheno_wordidxs) IN 
(SELECT DISTINCT
  s.* 
FROM
  genepheno_holdout_set s 
  LEFT JOIN 
  genepheno_pairs p 
    ON (s.doc_id = p.doc_id AND s.section_id = p.section_id AND s.sent_id = p.sent_id AND s.gene_wordidxs = STRING_TO_ARRAY(p.gene_wordidxs, '|~|')::INTEGER[] AND s.pheno_wordidxs = STRING_TO_ARRAY(p.pheno_wordidxs, '|~|')::INTEGER[]) WHERE p.doc_id IS NULL);

DELETE FROM genepheno_holdout_labels 
WHERE (doc_id, section_id, sent_id) NOT IN 
(SELECT DISTINCT doc_id, section_id, sent_id FROM genepheno_holdout_set);

DROP TABLE IF EXISTS sentences_input_with_holdout_gp;
CREATE TABLE sentences_input_with_holdout_gp AS (
  SELECT si.*
  FROM 
    sentences_input_with_gene_mention si
    JOIN genepheno_holdout_set s
      ON (si.doc_id = s.doc_id)
) DISTRIBUTED BY (doc_id);
"""
