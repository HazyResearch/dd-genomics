# `/code`: Database schema, data preparation/loading scripts, extractors UDFs, ... 

This directory contains most if not all the code.

## Files

* `parser2sentences.py`: Convert parser output files into a TSV file that can be
  loaded in the `sentences` table with the PostgreSQL `COPY FROM` command.

