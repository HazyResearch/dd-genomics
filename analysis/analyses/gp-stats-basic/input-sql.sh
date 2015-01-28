#!/usr/bin/env bash
# A script for seeing basic statistics about the number and type of gene mentions extracted
# Author: Alex Ratner <ajratner@stanford.edu>
# Created: 2015-01-25

# See: https://github.com/postgres/postgres/blob/master/src/include/catalog/pg_statistic.h

set -eu

# Generate the SQL for this task
echo "
  COPY (
    SELECT * FROM pg_statistic WHERE starelid=(
      SELECT oid FROM pg_class WHERE relname='gene_hpoterm_relations')
  ) TO STDOUT WITH CSV HEADER;
"
