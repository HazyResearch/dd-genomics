# `/code`: Database schema, data preparation/loading scripts, extractors UDFs, ... 

This directory contains most if not all the code.

## Files

* `copy_table_from_file.sh`: Load a TSV file into a database table with the
  PostgreSQL `COPY FROM` command.
* `create_schema.sh`: Create the database schema.
* `delete_from_table.sh`: Empty a database table with the PostgreSQL `DELETE
  FROM` command.
* `parser2sentences.py`: Convert parser output files into a TSV file that can be
  loaded in the `sentences` table with the PostgreSQL `COPY FROM` command.
* `run_parser2sentences.sh`: Run parser2sentences.py with the right paths from
  application.conf
* `schema.sql`: SQL script to build the schema. Used in `create_schema.sh`.

