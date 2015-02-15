#! /bin/bash

# Directory variables
# NOTE: if using mac, need to install coreutils / greadlink, or hardcode here...
DIRNAME=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
REAL_DIRNAME=`readlink -f ${DIRNAME}` || REAL_DIRNAME=`greadlink -f ${DIRNAME}`
export APP_HOME=$REAL_DIRNAME
export GDD_HOME=$APP_HOME

# Switch to python3
# TODO: do this in more proper fashion...?
unset PYTHONPATH
unset PYTHONHOME
export PATH=/lfs/local/0/senwu/software/python3/bin:$PATH
export PYTHONPATH="$PYTHONPATH:/lfs/local/0/senwu/software/"

#export PATH=/lfs/local/0/senwu/software/greenplum/greenplum-db/bin:$PATH
#source /lfs/local/0/senwu/software/greenplum/greenplum-db/greenplum_path.sh
#gpfdist -d /lfs/local/0/ajratner/data/gp_data -p 8082 -m 268435456 &
#ps aux | grep gpfdist

# TODO: change these variables for db connection, etc.
# TODO(alex): merge db/pg vars...
export HOSTNAME=raiders4

export PGHOST=${HOSTNAME}.stanford.edu
export DBHOST=$PGHOST
export GPHOST=$PGHOST

export PGPORT=6432
export DBPORT=$PGPORT
export GPPORT=8087

# NOTE: DDUSER & DBUSER might be different!
export DDUSER=ajratner
export DBUSER=senwu
export PGUSER=$DBUSER

export PGPASSWORD=${PGPASSWORD:-}

export DBNAME=genomics_recall

# TODO: set where to store the gp data
#export GPPATH=/lfs/${HOSTNAME}/0/senwu/develop/grounding
export GPPATH=/lfs/${HOSTNAME}/0/$DDUSER/data/gp_data

export LFS_DIR=/lfs/$HOSTNAME/0/$DDUSER


# TODO: set location of DeepDive local install!
export DEEPDIVE_HOME=$LFS_DIR/deepdive


# TODO: Machine Configuration
export MEMORY="256g"

export PARALLELISM=80

export SBT_OPTS="-Xmx$MEMORY"
export JAVA_OPTS="-Xmx$MEMORY"

# Using ddlib, analysis util lib
PYTHONPATH=$DEEPDIVE_HOME/ddlib:$DEEPDIVE_HOME/ddlib/ddlib:$REAL_DIRNAME/analysis/util:$PYTHONPATH
export LD_LIBRARY_PATH=$DEEPDIVE_HOME/lib/dw_linux/lib:$DEEPDIVE_HOME/lib/dw_linux/lib64
PATH=$PATH:$DEEPDIVE_HOME/ddlib
PATH=$PATH:$DEEPDIVE_HOME/sbt

# Other:
# The number of sentences in the sentences table
#export SENTENCES=95022507
# The input batch size for extractors working on the sentences table
#export SENTENCES_BATCH_SIZE=`echo  "(" ${SENTENCES} "/" ${PARALLELISM} ") + 1" | bc`
