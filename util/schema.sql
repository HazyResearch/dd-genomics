-- This SQL script contains the instruction to create the tables. 
-- WARNING: all the tables are dropped and recreated

-- Acronym table 
DROP TABLE IF EXISTS acronyms CASCADE;
CREATE TABLE acronyms (
	-- document id
	doc_id text,
	-- acronym
	acronym text,
	-- definitions
	definitions text[],
	-- is_correct
	is_correct boolean
) DISTRIBUTED BY (doc_id);

-- GeneRifs mentions
DROP TABLE IF EXISTS generifs_mentions CASCADE;
CREATE TABLE generifs_mentions (
	-- id for random variable (unused for generifs)
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
	-- is this a correct mention? (unused for generifs)
	is_correct boolean
) DISTRIBUTED BY (doc_id);

-- Gene Rifs mentions features
DROP TABLE IF EXISTS generifs_features CASCADE;
CREATE TABLE generifs_features (
	-- document id
	doc_id text,
	-- mention id
	mention_id text,
	-- feature
	feature text
) DISTRIBUTED BY (doc_id);

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

-- Gene / Phenotype relation mentions
DROP TABLE IF EXISTS genepheno_relations CASCADE;
CREATE TABLE genepheno_relations (
	-- id for random variable
	id bigint,
	-- document id
	doc_id text,
	-- gene mention sentence id
	sent_id_1 int,
	-- phenotype mention sentence id
	sent_id_2 int,
	-- relation id
	relation_id text,
	-- type
	type text,
	-- gene mention id
	mention_id_1 text,
	-- phenotype mention id
	mention_id_2 text,
	-- gene word indexes
	wordidxs_1 int[],
	-- phenotype word indexes
	wordidxs_2 int[],
	-- gene (words)
	words_1 text[],
	-- phenotype (words)
	words_2 text[],
	entity_1 text,
	entity_2 text,
	-- is this a correct relation?
	is_correct boolean
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

-- Gene / Phenotype relation facts
DROP TABLE IF EXISTS genepheno_facts CASCADE;
CREATE TABLE genepheno_facts (
	-- id for random variable
	id bigint,
  -- gene entity (gene symbol)
  gene text,
  -- phenotype entity (HPO ID)
  pheno text,
	-- is this a correct relation?
	is_correct boolean
) DISTRIBUTED BY (gene);

-- "Cheat" by getting gene / phenotype relations from this table
-- Should be sourced with a subset of true HPO relations
-- This models what we would extract from literature
DROP TABLE IF EXISTS genepheno_cheat CASCADE;
CREATE TABLE genepheno_cheat (
  -- gene entity (gene symbol)
  gene text,
  -- phenotype entity (HPO ID)
  pheno text
) DISTRIBUTED BY (gene);

-- Whether a pathway is relevant to a phenotype
DROP TABLE IF EXISTS pheno_pathway_relations CASCADE;
CREATE TABLE pheno_pathway_relations (
	-- id for random variable
	id bigint,
  -- phenotype entity (HPO ID)
  pheno text,
  -- Reactome pathway ID
  pathway_id text,
	-- is this a correct relation?
	is_correct boolean
) DISTRIBUTED BY (pheno);

-- Features for pathway and phenotype relevancy
DROP TABLE IF EXISTS pheno_pathway_features CASCADE;
CREATE TABLE pheno_pathway_features (
  -- phenotype entity (HPO ID)
  pheno text,
  -- Reactome pathway ID
  pathway_id text,
	-- feature
	feature text
) DISTRIBUTED BY (pheno);
