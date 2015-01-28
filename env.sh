#! /bin/bash

# TODO: change these variables for db connection (e.g. MindTagger, output metrics)
export DBHOST=raiders4.stanford.edu
export DBPORT=6432
export DBUSER=senwu
export DBNAME=genomics

# TODO: change these variables for running deep dive
export HOSTNAME=raiders4
export DDUSER=rionda
export PGPASSWORD=`cut -d':' -f 5 $HOME/.pgpass`

# Directory variables
DIRNAME=`dirname $0`
REAL_DIRNAME=`readlink -f ${DIRNAME}`

export DEEPDIVE_HOME=`cd ${REAL_DIRNAME}/../..; pwd`

export LFS_DIR=/lfs/$HOSTNAME/0/$DDUSER

export GPHOST=${HOSTNAME}.stanford.edu
export GPPORT=8888
export GPPATH=/lfs/${HOSTNAME}/0/$DDUSER/greenplum_gpfdist 

export APP_HOME=`pwd`

# Machine Configuration
export MEMORY="80g"
export PARALLELISM=90

# The number of sentences in the sentences table
export SENTENCES=95022507
# The input batch size for extractors working on the sentences table
export SENTENCES_BATCH_SIZE=`echo  "(" ${SENTENCES} "/" ${PARALLELISM} ") + 1" | bc`


# Database Configuration
# SBT Options
export SBT_OPTS="-Xmx$MEMORY"
export JAVA_OPTS="-Xmx$MEMORY"

# Using ddlib
PYTHONPATH=$DEEPDIVE_HOME/ddlib:$PYTHONPATH
