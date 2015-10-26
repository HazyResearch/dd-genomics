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