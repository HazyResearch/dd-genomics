#!/usr/bin/env bash
# A script for seeing basic statistics about the number and type of gene mentions extracted
# Author: Alex Ratner <ajratner@stanford.edu>
# Created: 2015-01-25
set -eu
ANALYSES_DIR=analyses

# check for command line args
if [ $# = 0 ]; then
  echo "Please list as args one or more of the following analysis tasks:"
  ls "$ANALYSES_DIR" | sed 's/^/  * /'
  false
fi

# loop through the analyses to be run
for task in "$@"; do
  echo "Running task $task:"

  # Make a new directory for the output analyses & runtime scripts
  dir=$(date +%Y%m%d)-$task
  if [[ -e $dir ]]; then
      suffix=2
      while [[ -e $dir.$suffix ]]; do
          let ++suffix
      done
      dir+=.$suffix
  fi
  mkdir -p $dir/.scripts

  # Generate the SQL for this task via the input-sql.sh script
  # TODO(alex): handle arguments for input-sql.sh correctly here!
  $ANALYSES_DIR/$task/input-sql.sh "$@" > $dir/.scripts/input.sql

  # Execute SQL
  echo "Executing SQL to $DBNAME database at $DBHOST..."
  psql -h $DBHOST -p $DBPORT -U $DBUSER $DBNAME \
    < $dir/.scripts/input.sql > $dir/output.csv

  # Run python post-processing script if present
  if [[ -e $ANALYSES_DIR/$task/process.py ]]; then
    echo "Post-processing with python..."
    python $ANALYSES_DIR/$task/process.py $dir/output.csv $dir/output
  fi
done
