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
) DISTRIBUTED BY (ensembl_id);

DROP INDEX IF EXISTS genes_ensembl_id;
CREATE INDEX genes_ensembl_id ON genes (ensembl_id);
DROP INDEX IF EXISTS genes_gene_name;
CREATE INDEX genes_gene_name ON genes (gene_name);

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
) DISTRIBUTED BY (doc_id, section_id);

DROP INDEX IF EXISTS gene_mentions_doc_id;
CREATE INDEX gene_mentions_doc_id ON gene_mentions (doc_id);
DROP INDEX IF EXISTS gene_mentions_section_id;
CREATE INDEX gene_mentions_section_id ON gene_mentions (section_id);
DROP INDEX IF EXISTS gene_mentions_sent_id;
CREATE INDEX gene_mentions_sent_id ON gene_mentions (sent_id);
DROP INDEX IF EXISTS gene_mentions_mention_id;
CREATE INDEX gene_mentions_mention_id ON gene_mentions (mention_id);

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
) DISTRIBUTED BY (doc_id, section_id);

DROP INDEX IF EXISTS variant_mentions_doc_id;
CREATE INDEX variant_mentions_doc_id ON variant_mentions (doc_id);
DROP INDEX IF EXISTS variant_mentions_section_id;
CREATE INDEX variant_mentions_section_id ON variant_mentions (section_id);
DROP INDEX IF EXISTS variant_mentions_sent_id;
CREATE INDEX variant_mentions_sent_id ON variant_mentions (sent_id);
DROP INDEX IF EXISTS variant_mentions_mention_id;
CREATE INDEX variant_mentions_mention_id ON variant_mentions (mention_id);

-- Gene mentions features
DROP TABLE IF EXISTS gene_features CASCADE;
CREATE TABLE gene_features (
	doc_id text,
        section_id text,
	mention_id text,
	feature text
) DISTRIBUTED BY (doc_id, section_id);

DROP INDEX IF EXISTS gene_features_doc_id;
CREATE INDEX gene_features_doc_id ON gene_features (doc_id);
DROP INDEX IF EXISTS gene_features_section_id;
CREATE INDEX gene_features_section_id ON gene_features (section_id);
DROP INDEX IF EXISTS gene_features_mention_id;
CREATE INDEX gene_features_mention_id ON gene_features (mention_id);

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

DROP INDEX IF EXISTS pheno_mentions_doc_id;
CREATE INDEX pheno_mentions_doc_id ON pheno_mentions (doc_id);
DROP INDEX IF EXISTS pheno_mentions_section_id;
CREATE INDEX pheno_mentions_section_id ON pheno_mentions (section_id);
DROP INDEX IF EXISTS pheno_mentions_sent_id;
CREATE INDEX pheno_mentions_sent_id ON pheno_mentions (sent_id);
DROP INDEX IF EXISTS pheno_mentions_mention_id;
CREATE INDEX pheno_mentions_mention_id ON pheno_mentions (mention_id);

-- Phenotype mentions features
DROP TABLE IF EXISTS pheno_features CASCADE;
CREATE TABLE pheno_features (
	doc_id text,
        section_id text,
	mention_id text,
	feature text
) DISTRIBUTED BY (doc_id, section_id);

DROP INDEX IF EXISTS pheno_features_doc_id;
CREATE INDEX pheno_features_doc_id ON pheno_features (doc_id);
DROP INDEX IF EXISTS pheno_features_section_id;
CREATE INDEX pheno_features_section_id ON pheno_features (section_id);
DROP INDEX IF EXISTS pheno_features_mention_id;
CREATE INDEX pheno_features_mention_id ON pheno_features (mention_id);

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
) DISTRIBUTED BY (doc_id, section_id);

DROP INDEX IF EXISTS genepheno_relations_doc_id;
CREATE INDEX genepheno_relations_doc_id ON genepheno_relations (doc_id);
DROP INDEX IF EXISTS genepheno_relations_section_id;
CREATE INDEX genepheno_relations_section_id ON genepheno_relations (section_id);
DROP INDEX IF EXISTS genepheno_relations_sent_id;
CREATE INDEX genepheno_relations_sent_id ON genepheno_relations (sent_id);
DROP INDEX IF EXISTS genepheno_relations_relation_id;
CREATE INDEX genepheno_relations_relation_id ON genepheno_relations (relation_id);
DROP INDEX IF EXISTS genepheno_relations_gene_mention_id;
CREATE INDEX genepheno_relations_gene_mention_id ON genepheno_relations (gene_mention_id);
DROP INDEX IF EXISTS genepheno_relations_pheno_mention_id;
CREATE INDEX genepheno_relations_pheno_mention_id ON genepheno_relations (pheno_mention_id);
DROP INDEX IF EXISTS genepheno_relations_gene_name;
CREATE INDEX genepheno_relations_gene_name ON genepheno_relations (gene_name);

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
) DISTRIBUTED BY (doc_id, section_id);

DROP INDEX IF EXISTS genepheno_association_doc_id;
CREATE INDEX genepheno_association_doc_id ON genepheno_association (doc_id);
DROP INDEX IF EXISTS genepheno_association_section_id;
CREATE INDEX genepheno_association_section_id ON genepheno_association (section_id);
DROP INDEX IF EXISTS genepheno_association_sent_id;
CREATE INDEX genepheno_association_sent_id ON genepheno_association (sent_id);
DROP INDEX IF EXISTS genepheno_association_relation_id;
CREATE INDEX genepheno_association_relation_id ON genepheno_association (relation_id);
DROP INDEX IF EXISTS genepheno_association_gene_mention_id;
CREATE INDEX genepheno_association_gene_mention_id ON genepheno_association (gene_mention_id);
DROP INDEX IF EXISTS genepheno_association_pheno_mention_id;
CREATE INDEX genepheno_association_pheno_mention_id ON genepheno_association (pheno_mention_id);
DROP INDEX IF EXISTS genepheno_association_gene_name;
CREATE INDEX genepheno_association_gene_name ON genepheno_association (gene_name);
 
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
) DISTRIBUTED BY (doc_id, section_id);

DROP INDEX IF EXISTS genepheno_causation_doc_id;
CREATE INDEX genepheno_causation_doc_id ON genepheno_causation (doc_id);
DROP INDEX IF EXISTS genepheno_causation_section_id;
CREATE INDEX genepheno_causation_section_id ON genepheno_causation (section_id);
DROP INDEX IF EXISTS genepheno_causation_sent_id;
CREATE INDEX genepheno_causation_sent_id ON genepheno_causation (sent_id);
DROP INDEX IF EXISTS genepheno_causation_relation_id;
CREATE INDEX genepheno_causation_relation_id ON genepheno_causation (relation_id);
DROP INDEX IF EXISTS genepheno_causation_gene_mention_id;
CREATE INDEX genepheno_causation_gene_mention_id ON genepheno_causation (gene_mention_id);
DROP INDEX IF EXISTS genepheno_causation_pheno_mention_id;
CREATE INDEX genepheno_causation_pheno_mention_id ON genepheno_causation (pheno_mention_id);
DROP INDEX IF EXISTS genepheno_causation_gene_name;
CREATE INDEX genepheno_causation_gene_name ON genepheno_causation (gene_name);

-- G/P relation mentions features
DROP TABLE IF EXISTS genepheno_features CASCADE;
CREATE TABLE genepheno_features (
	doc_id text,
        section_id text,
	relation_id text,
	feature text
) DISTRIBUTED BY (doc_id, section_id);

DROP INDEX IF EXISTS genepheno_features_doc_id;
CREATE INDEX genepheno_features_doc_id ON genepheno_features (doc_id);
DROP INDEX IF EXISTS genepheno_features_section_id;
CREATE INDEX genepheno_features_section_id ON genepheno_features (section_id);
DROP INDEX IF EXISTS genepheno_features_relation_id;
CREATE INDEX genepheno_features_relation_id ON genepheno_features (relation_id);

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
) DISTRIBUTED BY (doc_id, section1_id, section2_id);

DROP INDEX IF EXISTS genevariant_relations_doc_id;
CREATE INDEX genevariant_relations_doc_id ON genevariant_relations (doc_id);
DROP INDEX IF EXISTS genevariant_relations_section1_id;
CREATE INDEX genevariant_relations_section1_id ON genevariant_relations (section1_id);
DROP INDEX IF EXISTS genevariant_relations_section2_id;
CREATE INDEX genevariant_relations_section2_id ON genevariant_relations (section2_id);
DROP INDEX IF EXISTS genevariant_relations_sent1_id;
CREATE INDEX genevariant_relations_sent1_id ON genevariant_relations (sent1_id);
DROP INDEX IF EXISTS genevariant_relations_sent2_id;
CREATE INDEX genevariant_relations_sent2_id ON genevariant_relations (sent2_id);
DROP INDEX IF EXISTS genevariant_relations_relation_id;
CREATE INDEX genevariant_relations_relation_id ON genevariant_relations (relation_id);
DROP INDEX IF EXISTS genevariant_relations_gene_mention_id;
CREATE INDEX genevariant_relations_gene_mention_id ON genevariant_relations (gene_mention_id);
DROP INDEX IF EXISTS genevariant_relations_variant_mention_id;
CREATE INDEX genevariant_relations_variant_mention_id ON genevariant_relations (variant_mention_id);
DROP INDEX IF EXISTS genevariant_relations_gene_name;
CREATE INDEX genevariant_relations_gene_name ON genevariant_relations (gene_name);

DROP TABLE IF EXISTS genevariant_features CASCADE;
CREATE TABLE genevariant_features (
	doc_id text,
        section_id text,
	relation_id text,
	feature text
) DISTRIBUTED BY (doc_id, relation_id);

DROP INDEX IF EXISTS genevariant_features_doc_id;
CREATE INDEX genevariant_features_doc_id ON genevariant_features (doc_id);
DROP INDEX IF EXISTS genevariant_features_section_id;
CREATE INDEX genevariant_features_section_id ON genevariant_features (section_id);
DROP INDEX IF EXISTS genevariant_features_relation_id;
CREATE INDEX genevariant_features_relation_id ON genevariant_features (relation_id);

DROP TABLE IF EXISTS test_nlp;
CREATE TABLE test_nlp (id bigint) DISTRIBUTED BY (id);

DROP TABLE IF EXISTS plos_doi_to_pmid;
CREATE TABLE plos_doi_to_pmid (
  doi text,
  pmid text
) DISTRIBUTED BY (doi);

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
	entity text,
	words text[],
	is_correct boolean
) DISTRIBUTED BY (doc_id, section_id);

DROP INDEX IF EXISTS non_gene_acronyms_doc_id;
CREATE INDEX non_gene_acronyms_doc_id ON non_gene_acronyms (doc_id);
DROP INDEX IF EXISTS non_gene_acronyms_section_id;
CREATE INDEX non_gene_acronyms_section_id ON non_gene_acronyms (section_id);
DROP INDEX IF EXISTS non_gene_acronyms_sent_id;
CREATE INDEX non_gene_acronyms_sent_id ON non_gene_acronyms (sent_id);
DROP INDEX IF EXISTS non_gene_acronyms_mention_id;
CREATE INDEX non_gene_acronyms_mention_id ON non_gene_acronyms (mention_id);

-- Gene mentions features
DROP TABLE IF EXISTS non_gene_acronyms_features CASCADE;
CREATE TABLE non_gene_acronyms_features (
	doc_id text,
        section_id text,
	mention_id text,
	feature text
) DISTRIBUTED BY (doc_id, section_id);

DROP INDEX IF EXISTS non_gene_acronyms_features_doc_id;
CREATE INDEX non_gene_acronyms_features_doc_id ON non_gene_acronyms_features (doc_id);
DROP INDEX IF EXISTS non_gene_acronyms_features_section_id;
CREATE INDEX non_gene_acronyms_features_section_id ON non_gene_acronyms_features (section_id);
DROP INDEX IF EXISTS non_gene_acronyms_features_mention_id;
CREATE INDEX non_gene_acronyms_features_mention_id ON non_gene_acronyms_features (mention_id);

DROP TABLE IF EXISTS genepheno_holdout_set;
CREATE TABLE genepheno_holdout_set (
        doc_id text,
        section_id text,
        sent_id int,
        gene_wordidxs int[],
        pheno_wordidxs int[]
) DISTRIBUTED BY (doc_id, section_id);

DROP INDEX IF EXISTS genepheno_holdout_set_doc_id;
CREATE INDEX genepheno_holdout_set_doc_id ON genepheno_holdout_set (doc_id);
DROP INDEX IF EXISTS genepheno_holdout_set_section_id;
CREATE INDEX genepheno_holdout_set_section_id ON genepheno_holdout_set (section_id);
DROP INDEX IF EXISTS genepheno_holdout_set_sent_id;
CREATE INDEX genepheno_holdout_set_sent_id ON genepheno_holdout_set (sent_id);

DROP TABLE IF EXISTS genepheno_causation_canon CASCADE;
CREATE TABLE genepheno_causation_canon (
  hpo_id text,
  ensembl_id text
) DISTRIBUTED BY (hpo_id, ensembl_id);

DROP INDEX IF EXISTS genepheno_causation_canon_hpo_id;
CREATE INDEX genepheno_causation_canon_hpo_id ON genepheno_causation_canon (hpo_id);
DROP INDEX IF EXISTS genepheno_causation_canon_ensembl_id;
CREATE INDEX genepheno_causation_canon_ensembl_id ON genepheno_causation_canon (ensembl_id);

DROP TABLE IF EXISTS genepheno_association_canon CASCADE;
CREATE TABLE genepheno_association_canon (
  hpo_id text,
  ensembl_id text
) DISTRIBUTED BY (hpo_id, ensembl_id);

DROP INDEX IF EXISTS genepheno_association_canon_hpo_id;
CREATE INDEX genepheno_association_canon_hpo_id ON genepheno_association_canon (hpo_id);
DROP INDEX IF EXISTS genepheno_association_canon_ensembl_id;
CREATE INDEX genepheno_association_canon_ensembl_id ON genepheno_association_canon (ensembl_id);

DROP TABLE IF EXISTS hpo_abnormalities CASCADE;
CREATE TABLE hpo_abnormalities (
  hpo_id text,
  pheno_name text
) DISTRIBUTED BY (hpo_id);

DROP INDEX IF EXISTS hpo_abnormalities_hpo_id;
CREATE INDEX hpo_abnormalities_hpo_id ON hpo_abnormalities (hpo_id);

DROP TABLE IF EXISTS charite_canon CASCADE;
CREATE TABLE charite_canon (
  hpo_id text,
  ensembl_id text
);

DROP INDEX IF EXISTS charite_canon_hpo_id;
CREATE INDEX charite_canon_hpo_id ON charite_canon (hpo_id);
DROP INDEX IF EXISTS charite_canon_ensembl_id;
CREATE INDEX charite_canon_ensembl_id ON charite_canon (ensembl_id);

DROP TABLE IF EXISTS dummy CASCADE;
CREATE TABLE dummy (
  a int,
  b int,
  c int
);

-- DROP EXTENSION intarray;
-- CREATE EXTENSION intarray;
