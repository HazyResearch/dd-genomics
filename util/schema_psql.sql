-- This SQL script contains the instruction to create the tables. 
-- WARNING: all the tables are dropped and recreated

DROP TABLE IF EXISTS genes CASCADE;
CREATE TABLE genes (
  -- include primary key when dd fixes find command
  -- gene_id text primary key,
  ensembl_id text,
  canonical_name text,
  gene_name text,
  name_type text
) ;

-- Gene mentions
DROP TABLE IF EXISTS gene_mentions CASCADE;
CREATE TABLE gene_mentions (
	id bigint,
	doc_id text,
        section_id text,
	sent_id int,
	wordidxs int[],
	mention_id text,
        mapping_type text,
	supertype text,
        subtype text,
        gene_name text,
	words text[],
	is_correct boolean
) ;

-- Gene mentions
DROP TABLE IF EXISTS variant_mentions CASCADE;
CREATE TABLE variant_mentions (
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
) ;

-- Gene mentions features
DROP TABLE IF EXISTS gene_features CASCADE;
CREATE TABLE gene_features (
	doc_id text,
        section_id text,
	mention_id text,
	feature text
) ;

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
) ;

-- Phenotype mentions features
DROP TABLE IF EXISTS pheno_features CASCADE;
CREATE TABLE pheno_features (
	doc_id text,
        section_id text,
	mention_id text,
	feature text
) ;

DROP TABLE IF EXISTS variant_features CASCADE;
CREATE TABLE variant_features (
	doc_id text,
        section_id text,
	mention_id text,
	feature text
) ;

-- Gene / Phenotype mentions
DROP TABLE IF EXISTS genepheno_relations CASCADE;
CREATE TABLE genepheno_relations (
	id bigint,
	relation_id text,
	doc_id text,
        section_id text,
	sent_id int,
        gene_mention_id text,
        gene_name text,
        gene_wordidxs int[],
        gene_is_correct boolean,
	pheno_mention_id text,
        pheno_entity text,
        pheno_wordidxs int[],
        pheno_is_correct boolean
) ;

-- Gene / Phenotype association mentions
DROP TABLE IF EXISTS genepheno_association CASCADE;
CREATE TABLE genepheno_association (
	id bigint,
	relation_id text,
	doc_id text,
        section_id text,
	sent_id int,
        gene_mention_id text,
        gene_name text,
        gene_wordidxs int[],
	pheno_mention_id text,
        pheno_entity text,
        pheno_wordidxs int[],
	is_correct boolean,
        supertype text,
        subtype text
) ;

-- Gene / Phenotype association mentions
DROP TABLE IF EXISTS genepheno_causation CASCADE;
CREATE TABLE genepheno_causation (
	id bigint,
	relation_id text,
	doc_id text,
        section_id text,
	sent_id int,
        gene_mention_id text,
        gene_name text,
        gene_wordidxs int[],
	pheno_mention_id text,
        pheno_entity text,
        pheno_wordidxs int[],
	is_correct boolean,
        supertype text,
        subtype text
) ;

-- G/P relation mentions features
DROP TABLE IF EXISTS genepheno_features CASCADE;
CREATE TABLE genepheno_features (
	doc_id text,
        section_id text,
	relation_id text,
	feature text
) ;

-- Gene / Variant mentions
DROP TABLE IF EXISTS genevariant_relations CASCADE;
CREATE TABLE genevariant_relations (
	id bigint,
	relation_id text,
	doc_id text,
        section1_id text,
	sent1_id int,
        section2_id text,
	sent2_id int,
	variant_mention_id text,
        variant_entity text,
        variant_wordidxs int[],
        variant_is_correct boolean,
        gene_mention_id text,
        gene_name text,
        gene_wordidxs int[],
        gene_is_correct boolean,
	is_correct boolean,
        supertype text,
        subtype text
) ;

DROP TABLE IF EXISTS genevariant_features CASCADE;
CREATE TABLE genevariant_features (
	doc_id text,
        section_id text,
	relation_id text,
	feature text
) ;

DROP TABLE IF EXISTS test_nlp;
CREATE TABLE test_nlp (id bigint) ;

DROP TABLE IF EXISTS plos_doi_to_pmid;
CREATE TABLE plos_doi_to_pmid (
  doi text,
  pmid text
) ;

DROP TABLE IF EXISTS non_gene_acronyms CASCADE;
CREATE TABLE non_gene_acronyms (
	-- id for random variable
	id bigint,
	doc_id text,
        section_id text,
	sent_id int,
	short_wordidxs int[],
	long_wordidxs int[],
	mention_id text,
	supertype text,
        subtype text,
	abbrev text,
	definition text[],
	is_correct boolean
) ;

-- Gene mentions features
DROP TABLE IF EXISTS non_gene_acronyms_features CASCADE;
CREATE TABLE non_gene_acronyms_features (
	doc_id text,
        section_id text,
	mention_id text,
	feature text
) ;

DROP TABLE IF EXISTS pheno_acronyms CASCADE;
CREATE TABLE pheno_acronyms (
	-- id for random variable
	id bigint,
	doc_id text,
        section_id text,
	sent_id int,
	short_wordidxs int[],
	long_wordidxs int[],
	mention_id text,
	supertype text,
        subtype text,
	abbrev text,
	definition text[],
        entity text,
	is_correct boolean
) ;

-- Gene mentions features
DROP TABLE IF EXISTS pheno_acronyms_features CASCADE;
CREATE TABLE pheno_acronyms_features (
	doc_id text,
        section_id text,
	mention_id text,
	feature text
) ;

DROP TABLE IF EXISTS genepheno_holdout_set;
CREATE TABLE genepheno_holdout_set (
        doc_id text,
        section_id text,
        sent_id int,
        gene_wordidxs int[],
        pheno_wordidxs int[]
) ;

DROP TABLE IF EXISTS genepheno_holdout_labels;
CREATE TABLE genepheno_holdout_labels (
  doc_id text,
  section_id text,
  sent_id int,
  is_correct text,
  type text,
  labeler text
);

DROP TABLE IF EXISTS genepheno_causation_canon CASCADE;
CREATE TABLE genepheno_causation_canon (
  hpo_id text,
  ensembl_id text
) ;

DROP TABLE IF EXISTS genepheno_association_canon CASCADE;
CREATE TABLE genepheno_association_canon (
  hpo_id text,
  ensembl_id text
) ;

DROP TABLE IF EXISTS hpo_abnormalities CASCADE;
CREATE TABLE hpo_abnormalities (
  hpo_id text,
  pheno_name text
) ;

DROP TABLE IF EXISTS charite_canon CASCADE;
CREATE TABLE charite_canon (
  hpo_id text,
  ensembl_id text
);

DROP TABLE IF EXISTS charite CASCADE;
CREATE TABLE charite (
  hpo_id text,
  ensembl_id text,
  source text
);

DROP TABLE IF EXISTS dummy CASCADE;
CREATE TABLE dummy (
  a int,
  b int,
  c int
);

