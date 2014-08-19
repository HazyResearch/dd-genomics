-- This SQL script contains the instruction to create the tables. 
-- WARNING: all the tables are dropped and recreated

-- Sentences table
DROP TABLE IF EXISTS sentences CASCADE;
CREATE TABLE sentences (
	-- document id
	docid text,
	-- sentence id
	sentid int,
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

-- Gene mentions
DROP TABLE IF EXISTS genes_mentions CASCADE;
CREATE TABLE genes_mentions (
	-- id for random variable
	id bigint,
	-- mention id
	mentionid text,
	-- entity name
	name text,
	-- provenance
	provenance text[],
	-- is this a correct mention? (for training)
	is_correct boolean
);

-- HPO terms mentions
DROP TABLE IF EXISTS hpoterms_mentions CASCADE;
CREATE TABLE hpoterms_mentions (
	-- id for random variable
	id bigint,
	-- mention id
	mentionid text,
	-- entity name
	name text,
	-- provenance
	provenance text[],
	-- is this a correct mention? (for training)
	is_correct boolean
);

-- 'gene <-> HPO term' relations
DROP TABLE IF EXISTS gene_hpoterm_relations CASCADE;
CREATE TABLE gene_hpoterm_relations (
);
        
