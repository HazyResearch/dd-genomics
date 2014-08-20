-- This SQL script contains the instruction to create the tables. 
-- WARNING: all the tables are dropped and recreated

-- Sentences table
-- DROP TABLE IF EXISTS sentences CASCADE;
-- CREATE TABLE sentences (
-- 	-- document id
-- 	doc_id text,
-- 	-- sentence id
-- 	sent_id int,
-- 	-- word indexes
-- 	wordidxs int[],
-- 	-- words
-- 	words text[],
-- 	-- parts of speech
-- 	poses text[],
-- 	-- named entity recognition tags
-- 	ners text[],
-- 	-- lemmified version of words
-- 	lemmas text[],
-- 	-- dependency path labels
-- 	dep_paths text[],
-- 	-- dependency path parents
-- 	dep_parents int[],
-- 	-- bounding boxes
-- 	bounding_boxes text[]
-- );

-- Gene mentions
DROP TABLE IF EXISTS genes_mentions CASCADE;
CREATE TABLE genes_mentions (
	-- id for random variable
	id bigint,
	-- document id
	doc_id text,
	-- sentence id
	sent_id int,
	-- mention id
	mention_id text,
	-- start word id
	start_word_id int,
	-- end word id
	end_word_id int,
	-- mention type
	type text,
	-- is this a correct mention?
	is_correct boolean,
	-- string representation
	repr text,
	-- features for training
	features text[],
	-- serialized object
	object text
);

-- HPO terms mentions
DROP TABLE IF EXISTS hpoterms_mentions CASCADE;
CREATE TABLE hpoterms_mentions (
	-- id for random variable
	id bigint,
	-- document id
	doc_id text,
	-- sentence id
	sent_id int,
	-- mention id
	mention_id text,
	-- start word id
	start_word_id int,
	-- end word id
	end_word_id int,
	-- mention type
	type text,
	-- is this a correct mention?
	is_correct boolean,
	-- string representation
	repr text,
	-- features for training
	features text[],
	-- serialized object
	object text
);

-- Gene / HPOterm relation mentions
DROP TABLE IF EXISTS gene_hpoterm_relations CASCADE;
CREATE TABLE gene_hpoterm_relations (
	-- id for random variable
	id bigint,
	-- type
	type text,
	-- mention 1
	mention_1 text,
	-- mention 2
	mention_2 text,
	-- is this a correct relation?
	is_correct boolean,
	-- features for training
	features text[]
);

