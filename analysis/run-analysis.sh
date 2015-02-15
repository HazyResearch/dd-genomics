#!/usr/bin/env bash
# A script for seeing basic statistics about the number and type of gene mentions extracted
# Author: Alex Ratner <ajratner@stanford.edu>
# Created: 2015-01-25
set -eu
if [[ -e ../env.sh ]]; then
  source ../env.sh
else
  source env.sh
fi
DIR_MAIN=$GDD_HOME/analysis
DIR_SCRIPTS=$DIR_MAIN/analyses

[[ $# -eq 2 ]] || {
  echo "Usage: $0 NAME MODE"
  echo " where NAME is one of g (gene), p (phenotype), gp (gene-phenotype)"
  echo " where MODE is one of:"
  ls "$DIR_SCRIPTS" | sed 's/^/  * /'
  false
}
n=$1; shift
mode=$1; shift

# TODO(alex): change for new names post-dd run!
case $n in
g)
  name="gene_mentions"
  ;;
p)
  name="hpoterm_mentions"
  ;;
gp)
  name="gene_hpoterm_relations"
  ;;
esac

# run the task
echo "Running $mode analysis for $name:"

# Make a new directory for the output analyses & runtime scripts
dir=$DIR_MAIN/$(date +%Y%m%d)-$name-$mode
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
$DIR_SCRIPTS/$mode/input-sql.sh $name "$@" > $dir/.scripts/input.sql

# Execute SQL
echo "Executing SQL to $DBNAME database at $DBHOST..."
psql -h $DBHOST -p $DBPORT -U $DBUSER $DBNAME \
  < $dir/.scripts/input.sql > $dir/output.csv

# Run python post-processing script if present
if [[ -e $DIR_SCRIPTS/$mode/process.py ]]; then
  echo "Post-processing with python..."
  python $DIR_SCRIPTS/$mode/process.py $dir/output.csv $dir/output $name
fi
