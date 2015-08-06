-- This SQL script contains the instruction to create the tables. 
-- WARNING: all the tables are dropped and recreated

-- Gene mentions
DROP TABLE IF EXISTS gene_mentions CASCADE;
CREATE TABLE gene_mentions (
	id bigint,
	doc_id text,
        section_id text,
	sent_id int,
	wordidxs int[],
	mention_id text,
	supertype text,
        subtype text,
	entity text,
	words text[],
	is_correct boolean
) DISTRIBUTED BY (doc_id, section_id);

-- Gene mentions
DROP TABLE IF EXISTS genevar_mentions CASCADE;
CREATE TABLE genevar_mentions (
	id bigint,
	doc_id text,
        section_id text,
	sent_id int,
	wordidxs int[],
	mention_id text,
	supertype text,
        subtype text,
	entity text,
	words text[],
	is_correct boolean
) DISTRIBUTED BY (doc_id, section_id);

-- Gene mentions features
DROP TABLE IF EXISTS gene_features CASCADE;
CREATE TABLE gene_features (
	doc_id text,
        section_id text,
	mention_id text,
	feature text
) DISTRIBUTED BY (doc_id, section_id);

-- phenotype mentions
DROP TABLE IF EXISTS pheno_mentions CASCADE;
CREATE TABLE pheno_mentions (
	id bigint,
	doc_id text,
        section_id text,
	sent_id int,
	wordidxs int[],
	mention_id text,
	supertype text,
        subtype text,
	entity text,
	words text[],
	is_correct boolean
) DISTRIBUTED BY (doc_id, section_id);

-- Phenotype mentions features
DROP TABLE IF EXISTS pheno_features CASCADE;
CREATE TABLE pheno_features (
	doc_id text,
        section_id text,
	mention_id text,
	feature text
) DISTRIBUTED BY (doc_id, section_id);

-- Gene / Phenotype mentions
DROP TABLE IF EXISTS genepheno_relations CASCADE;
CREATE TABLE genepheno_relations (
	id bigint,
	relation_id text,
	doc_id text,
        section_id text,
	sent_id int,
	gene_mention_id text,
        gene_entity text,
        gene_wordidxs int[],
        gene_is_correct boolean,
	pheno_mention_id text,
        pheno_entity text,
        pheno_wordidxs int[],
        pheno_is_correct boolean
) DISTRIBUTED BY (doc_id, section_id);

-- Gene / Phenotype association mentions
DROP TABLE IF EXISTS genepheno_association CASCADE;
CREATE TABLE genepheno_association (
	id bigint,
	relation_id text,
	doc_id text,
        section_id text,
	sent_id int,
	gene_mention_id text,
        gene_entity text,
        gene_wordidxs int[],
	pheno_mention_id text,
        pheno_entity text,
        pheno_wordidxs int[],
	is_correct boolean,
        supertype text,
        subtype text
) DISTRIBUTED BY (doc_id, section_id);
 
-- Gene / Phenotype association mentions
DROP TABLE IF EXISTS genepheno_causation CASCADE;
CREATE TABLE genepheno_causation (
	id bigint,
	relation_id text,
	doc_id text,
        section_id text,
	sent_id int,
	gene_mention_id text,
        gene_entity text,
        gene_wordidxs int[],
	pheno_mention_id text,
        pheno_entity text,
        pheno_wordidxs int[],
	is_correct boolean,
        supertype text,
        subtype text
) DISTRIBUTED BY (doc_id, section_id);

-- G/P relation mentions features
DROP TABLE IF EXISTS genepheno_features CASCADE;
CREATE TABLE genepheno_features (
	doc_id text,
        section_id text,
	relation_id text,
	feature text
) DISTRIBUTED BY (doc_id, section_id);

-- Gene / Phenotype mentions
DROP TABLE IF EXISTS genevarpheno_relations CASCADE;
CREATE TABLE genevarpheno_relations (
	id bigint,
	relation_id text,
	doc_id text,
        section_id text,
	sent_id int,
	genevar_mention_id text,
        genevar_entity text,
        genevar_wordidxs int[],
        genevar_is_correct boolean,
	pheno_mention_id text,
        pheno_entity text,
        pheno_wordidxs int[],
        pheno_is_correct boolean
) DISTRIBUTED BY (doc_id, section_id);

DROP TABLE IF EXISTS test_nlp;
CREATE TABLE test_nlp (id bigint);

DROP TABLE IF EXISTS plos_doi_to_pmid;
CREATE TABLE plos_doi_to_pmid (
  doi text,
  pmid text
) DISTRIBUTED BY (doi);
