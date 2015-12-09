#! /usr/bin/env bash

deepdive sql """
        DELETE FROM doc_metadata
        WHERE (doc_id in (
          SELECT doc_id FROM doc_metadata WHERE issn_print <> 'null'
        )
        AND issn_print = 'null'
        );"""

deepdive sql """
        DELETE FROM doc_metadata
        WHERE (doc_id in (
          SELECT doc_id FROM doc_metadata WHERE issn_electronic <> 'null'
        )
        AND issn_electronic = 'null' AND issn_print = 'null'
        ); """

deepdive sql """
        DELETE FROM doc_metadata
        WHERE (doc_id in (
          SELECT doc_id FROM doc_metadata WHERE issn_global <> 'null'
        )
        AND issn_global = 'null' AND issn_print = 'null' AND issn_electronic = 'null'
        ); """

deepdive sql """
        DELETE FROM doc_metadata
        WHERE (doc_id in (
          SELECT doc_id FROM doc_metadata WHERE doc_id !~ '^[0-9]+' GROUP BY doc_id HAVING count(doc_id) >= 3
        )
        );
      """


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