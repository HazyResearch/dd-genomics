-- This SQL script contains the instruction to create the tables. 
-- WARNING: all the tables are dropped and recreated

-- Sentences table
DROP TABLE IF EXISTS sentences CASCADE;
CREATE TABLE sentences (
  doc_id text,
  section_id text,
  sent_id int,
  ref_doc_id text,
  words text[],
  lemmas text[],
  poses text[],
  ners text[],
  dep_paths text[],
  dep_parents int[]
 ) DISTRIBUTED BY (doc_id, section_id);

-- Sentences table in concatentated string format
DROP TABLE IF EXISTS sentences_input CASCADE;
CREATE TABLE sentences_input (
  doc_id text,
  section_id text,
  sent_id int,
  ref_doc_id text,
  words text,
  lemmas text,
  poses text,
  ners text,
  dep_paths text,
  dep_parents text
 ) DISTRIBUTED BY (doc_id, section_id);

-- Distantly supervision via MeSH: HPO to document map
DROP TABLE IF EXISTS hpo_to_doc_via_mesh CASCADE;
CREATE TABLE hpo_to_doc_via_mesh (
  hpo_id text,
  doc_id text
) DISTRIBUTED BY (hpo_id, doc_id);

DROP TABLE IF EXISTS document_metadata CASCADE;
CREATE TABLE document_metadata (
  doc_id text,
  source text,
  year int
)
