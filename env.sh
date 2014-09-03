#! /bin/bash

DIRNAME=`dirname $0`
REAL_DIRNAME=`readlink -f ${DIRNAME}`

export DEEPDIVE_HOME=`cd ${REAL_DIRNAME}/../..; pwd`

export HOSTNAME=`hostname`
export LFS_DIR=/lfs/$HOSTNAME/0/rionda/

export APP_HOME=`pwd`

# Machine Configuration
export MEMORY="256g"
export PARALLELISM=70

# The number of sentences in the sentences table
export SENTENCES=95027000
# The input batch size for extractors working on the sentences table
export SENTENCES_BATCH_SIZE=`echo  "(" ${SENTENCES} "/" ${PARALLELISM} ") + 1" | bc`


# Database Configuration
export DBNAME=genomics
export PGPASSWORD=`cut -d':' -f 5 $HOME/.pgpass`
# SBT Options
export SBT_OPTS="-Xmx$MEMORY"
export JAVA_OPTS="-Xmx$MEMORY"

# Using ddlib
PYTHONPATH=$DEEPDIVE_HOME/ddlib:$PYTHONPATH

