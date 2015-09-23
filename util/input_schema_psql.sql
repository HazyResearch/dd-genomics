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
 ) ;

-- DROP INDEX IF EXISTS sentences_doc_id;
-- CREATE INDEX sentences_doc_id ON sentences (doc_id);
-- DROP INDEX IF EXISTS sentences_section_id;
-- CREATE INDEX sentences_section_id ON sentences (section_id);
-- DROP INDEX IF EXISTS sentences_sent_id;
-- CREATE INDEX sentences_sent_id ON sentences (sent_id);
-- DROP INDEX IF EXISTS sentences_ref_doc_id;
-- CREATE INDEX sentences_ref_doc_id ON sentences (ref_doc_id);


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
 ) ;

-- DROP INDEX IF EXISTS sentences_input_doc_id;
-- CREATE INDEX sentences_input_doc_id ON sentences_input (doc_id);
-- DROP INDEX IF EXISTS sentences_input_section_id;
-- CREATE INDEX sentences_input_section_id ON sentences_input (section_id);
-- DROP INDEX IF EXISTS sentences_input_sent_id;
-- CREATE INDEX sentences_input_sent_id ON sentences_input (sent_id);
-- DROP INDEX IF EXISTS sentences_input_ref_doc_id;
-- CREATE INDEX sentences_input_ref_doc_id ON sentences_input (ref_doc_id);

-- Distantly supervision via MeSH: HPO to document map
DROP TABLE IF EXISTS hpo_to_doc_via_mesh CASCADE;
CREATE TABLE hpo_to_doc_via_mesh (
  hpo_id text,
  doc_id text
) ;


