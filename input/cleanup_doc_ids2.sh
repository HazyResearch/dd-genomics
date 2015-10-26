#! /usr/bin/env bash

#Version to be used in greenplum with distributed by
#deepdive sql """
#        DROP TABLE IF EXISTS doc_metadata_uniq CASCADE;
#        ALTER TABLE doc_metadata RENAME TO doc_metadata_uniq;
#        CREATE TABLE doc_metadata AS (SELECT * FROM doc_metadata_uniq LIMIT 1) DISTRIBUTED BY (doc_id);
#        TRUNCATE TABLE doc_metadata;
#        INSERT INTO doc_metadata (SELECT DISTINCT ON (doc_id) * FROM doc_metadata_uniq);
#      """

deepdive sql """
  DROP TABLE IF EXISTS doc_metadata_uniq CASCADE;
  ALTER TABLE doc_metadata RENAME TO doc_metadata_uniq;
  CREATE TABLE doc_metadata AS (SELECT * FROM doc_metadata_uniq LIMIT 1);
  TRUNCATE TABLE doc_metadata;
  INSERT INTO doc_metadata (SELECT DISTINCT ON (doc_id) * FROM doc_metadata_uniq);
      """