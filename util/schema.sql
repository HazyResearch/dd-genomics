-- This SQL script contains the instruction to create the tables. 
-- WARNING: all the tables are dropped and recreated

-- Gene mentions
DROP TABLE IF EXISTS gene_mentions CASCADE;
CREATE TABLE gene_mentions (
	-- id for random variable
	id bigint,
	-- document id
	doc_id text,
	-- sentence id
	sent_id int,
	-- indexes of the words composing the mention
	wordidxs int[],
	-- mention id
	mention_id text,
	-- mention type
	type text,
	-- entity
	entity text,
	-- words
	words text[],
	-- is this a correct mention?
	is_correct boolean
) DISTRIBUTED BY (doc_id);

-- Gene mentions features
DROP TABLE IF EXISTS gene_features CASCADE;
CREATE TABLE gene_features (
	-- document id
	doc_id text,
	-- mention id
	mention_id text,
	-- feature
	feature text
) DISTRIBUTED BY (doc_id);

-- phenotype mentions
DROP TABLE IF EXISTS pheno_mentions CASCADE;
CREATE TABLE pheno_mentions (
	-- id for random variable
	id bigint,
	-- document id
	doc_id text,
	-- sentence id
	sent_id int,
	-- indexes of the words composing the mention
	wordidxs int[],
	-- mention id
	mention_id text,
	-- mention type
	type text,
	-- entity
	entity text,
	-- words
	words text[],
	-- is this a correct mention?
	is_correct boolean
) DISTRIBUTED BY (doc_id);

-- Phenotype mentions features
DROP TABLE IF EXISTS pheno_features CASCADE;
CREATE TABLE pheno_features (
	-- document id
	doc_id text,
	-- mention id
	mention_id text,
	-- feature
	feature text
) DISTRIBUTED BY (doc_id);

-- Gene / Phenotype mentions
DROP TABLE IF EXISTS genepheno_relations CASCADE;
CREATE TABLE genepheno_relations (
	-- id for random variable
	id bigint,
	-- relation id
	relation_id text,
	-- document id
	doc_id text,
        -- sentence id
	sent_id int,
	-- gene mention id
	gene_mention_id text,
        -- gene entity
        gene_entity text,
        -- gene word indexes
        gene_wordidxs int[],
	-- phenotype mention id
	pheno_mention_id text,
        -- pheno entity
        pheno_entity text,
        -- pheno word indexes
        pheno_wordidxs int[],
	-- length of g-p dependency path; -1 if no or bat dep. path
        dep_path_len int
) DISTRIBUTED BY (doc_id);

-- Gene / Phenotype association mentions
DROP TABLE IF EXISTS genepheno_association CASCADE;
CREATE TABLE genepheno_association (
	-- id for random variable
	id bigint,
	-- relation id
	relation_id text,
	-- document id
	doc_id text,
        -- sentence id
	sent_id int,
	-- gene mention id
	gene_mention_id text,
        -- gene entity
        gene_entity text,
        -- gene word indexes
        gene_wordidxs int[],
	-- phenotype mention id
	pheno_mention_id text,
        -- pheno entity
        pheno_entity text,
        -- pheno word indexes
        pheno_wordidxs int[],
	-- is it an associative relationship?
	is_correct boolean,
        type text
) DISTRIBUTED BY (doc_id);
 
-- Gene / Phenotype association mentions
DROP TABLE IF EXISTS genepheno_causation CASCADE;
CREATE TABLE genepheno_causation (
	-- id for random variable
	id bigint,
	-- relation id
	relation_id text,
	-- document id
	doc_id text,
        -- sentence id
	sent_id int,
	-- gene mention id
	gene_mention_id text,
        -- gene entity
        gene_entity text,
        -- gene word indexes
        gene_wordidxs int[],
	-- phenotype mention id
	pheno_mention_id text,
        -- pheno entity
        pheno_entity text,
        -- pheno word indexes
        pheno_wordidxs int[],
	-- is it a causative relationship?
	is_correct boolean,
        type text
) DISTRIBUTED BY (doc_id);

-- G/P relation mentions features
DROP TABLE IF EXISTS genepheno_features CASCADE;
CREATE TABLE genepheno_features (
	-- document id
	doc_id text,
	-- relation id
	relation_id text,
	-- feature
	feature text
) DISTRIBUTED BY (doc_id);

DROP TABLE IF EXISTS test_nlp;
CREATE TABLE test_nlp (id bigint);
