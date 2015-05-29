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

-- Distantly supervision via MeSH: HPO to document map
DROP TABLE IF EXISTS hpo_to_doc_via_mesh CASCADE;
CREATE TABLE hpo_to_doc_via_mesh (
  -- HPO ID
  hpo_id text,
  -- Document ID
  doc_id text
);
