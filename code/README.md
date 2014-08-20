# `/code`: Database schema, data preparation/loading scripts, extractors UDFs, ... 

This directory contains most if not all the code.

## Data preparation / Table management

* `copy_table_from_file.sh`: Load a TSV file into a database table with the
  PostgreSQL `COPY FROM` command.
* `create_schema.sh`: Create the database schema.
* `delete_from_table.sh`: Empty a database table with the PostgreSQL `DELETE
  FROM` command.
* `get_parser_outputs.sh`: Extract the parser outputs from the article directory
  and link them to files named after the article.
* `parser2sentences.py`: Convert parser output files into a TSV file that can be
  loaded in the `sentences` table with the PostgreSQL `COPY FROM` command.
* `run_parser2sentences.sh`: Run parser2sentences.py with the right paths from
  application.conf
* `schema.sql`: SQL script to build the schema. Used in `create_schema.sh`.

## Extractors

* `dstruct/` directory: Contains classes to model sentences, words, and
  mentions.
* `extractors/` directory: Contains classes to model extractors. These classes
  do the real 'grunt work'.
* `gene_hpoterm_relations.py`: Extract relation mentions between genes and HPO
  terms. Basically calls `extractors/RelationExtractor_GeneHPOterm.py`.
* `genes_mentions_local.py`: Extract mentions of genes at the 'local' (sentence)
  level. Basically calls `extractors/MentionExtractor_Gene.py`.
* `hpoterms_mentions_local.py`: Extract mentions of HPO terms at the 'local'
  (sentence) level. Basically calls `extractors/MentionExtractor_HPOterm.py`.


