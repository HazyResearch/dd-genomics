# `/code`: Database schema, data preparation/loading scripts, extractors UDFs, ... 

This directory contains most if not all the code.

## Files

* `malt2sentences.py`: Convert Malt output files into a TSV file that can be
  loaded in the `sentence` table with the PostgreSQL `COPY FROM` command.

