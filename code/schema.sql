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
 );

-- Gene mentions (without supervision)
DROP TABLE IF EXISTS gene_mentions CASCADE;
CREATE TABLE gene_mentions (
	-- id for random variable
	id bigint,
	-- document id
	doc_id text,
	-- sentence id
	sent_id int,
	-- start word id
	start_word_idx int,
	-- end word id
	end_word_idx int,
	-- mention id
	mention_id text,
	-- mention type
	type text,
	-- entity
	entity text,
	-- words
	words text[],
	-- is this a correct mention?
	is_correct boolean,
	-- features for training
	features text[]
);

-- Supervised and non supervised Gene mentions
DROP TABLE IF EXISTS supervised_gene_mentions CASCADE;
CREATE TABLE supervised_gene_mentions (
	-- id for random variable
	id bigint,
	-- document id
	doc_id text,
	-- sentence id
	sent_id int,
	-- start word id
	start_word_idx int,
	-- end word id
	end_word_idx int,
	-- mention id
	mention_id text,
	-- mention type
	type text,
	-- entity
	entity text,
	-- words
	words text[],
	-- is this a correct mention?
	is_correct boolean,
	-- features for training
	features text[]
);

-- HPO terms mentions
DROP TABLE IF EXISTS hpoterm_mentions CASCADE;
CREATE TABLE hpoterm_mentions (
	-- id for random variable
	id bigint,
	-- document id
	doc_id text,
	-- sentence id
	sent_id int,
	-- start word id
	start_word_idx int,
	-- end word id
	end_word_idx int,
	-- mention id
	mention_id text,
	-- mention type
	type text,
	-- entity
	entity text,
	-- words
	words text[],
	-- is this a correct mention?
	is_correct boolean,
	-- features for training
	features text[]
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

