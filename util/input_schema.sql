-- This SQL script contains the instruction to create the tables. 
-- WARNING: all the tables are dropped and recreated


-- Sentences table
DROP TABLE IF EXISTS sentences CASCADE;
CREATE TABLE sentences (
 	-- document id
 	doc_id text,
 	-- sentence id
 	sent_id int,
 	-- word indexes
 	wordidxs int[],
 	-- words
 	words text[],
 	-- parts of speech
 	poses text[],
 	-- named entity recognition tags
 	ners text[],
 	-- lemmified version of words
 	lemmas text[],
 	-- dependency path labels
 	dep_paths text[],
 	-- dependency path parents
 	dep_parents int[],
 	-- bounding boxes
 	bounding_boxes text[]
 ) DISTRIBUTED BY (doc_id);

-- Sentences table in concatentated string format
DROP TABLE IF EXISTS sentences_input CASCADE;
CREATE TABLE sentences_input (
 	-- document id
 	doc_id text,
 	-- sentence id
 	sent_id int,
 	-- word indexes
 	wordidxs text,
 	-- words
 	words text,
 	-- parts of speech
 	poses text,
 	-- named entity recognition tags
 	ners text,
 	-- lemmified version of words
 	lemmas text,
 	-- dependency path labels
 	dep_paths text,
 	-- dependency path parents
 	dep_parents text,
 	-- bounding boxes
 	bounding_boxes text
 ) DISTRIBUTED BY (doc_id);

-- GeneRifs table
DROP TABLE IF EXISTS generifs CASCADE;
CREATE TABLE generifs (
	-- document id
	doc_id text,
	-- sentence id
	sent_id int,
	-- word indexes
	wordidxs int[],
	-- words
	words text[],
	-- parts of speech
	poses text[],
	-- named entity recognition tags
	ners text[],
	-- lemmified version of words
	lemmas text[],
	-- dependency path labels
	dep_paths text[],
	-- dependency path parents
	dep_parents int[],
	-- bounding boxes
	bounding_boxes text[],
	-- 'labelled' gene that is contained in the geneRif
	gene text
) DISTRIBUTED BY (doc_id);

-- HPO phenotype DAG
DROP TABLE IF EXISTS hpo_dag CASCADE;
CREATE TABLE hpo_dag (
  -- parent HPO ID
  parent text,
  -- child HPO ID
  child text,
  -- Is 'child' a child of 'Phenotypic Abnormality' (HP:0000118)
  is_pheno boolean
);

-- Reactome pathways
DROP TABLE IF EXISTS reactome_pathways CASCADE;
CREATE TABLE reactome_pathways (
  -- pathway (Reactome ID)
  pathway_id text,
  -- gene (HGNC symbol)
  gene text,
  -- pathway name
  pathway_name text
);
