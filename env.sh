#! /bin/bash

# TODO: Specify these variables according to your system configuration!
export DDUSER=         # the user running the application
export DBUSER=$DDUSER  # the user logging in to the db- default is same as DDUSER
export DBNAME=         # the name of the application database
export PGHOST=         # the server running the database
export PGPORT=         # the database access port
export GPPORT=         # the port that gpfdist is running on

# TODO: Machine Configuration
export MEMORY="256g"
export PARALLEL_GROUNDING="true"
export PARALLELISM=80
export SBT_OPTS="-Xmx$MEMORY"
export JAVA_OPTS="-Xmx$MEMORY"

# Directory variables
# NOTE: if using mac, need to install coreutils / greadlink, or hardcode here...
DIRNAME=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
REAL_DIRNAME=`readlink -f ${DIRNAME}` || REAL_DIRNAME=`greadlink -f ${DIRNAME}`
export APP_HOME=$REAL_DIRNAME
export GDD_HOME=$APP_HOME
export DEEPDIVE_HOME=/lfs/local/0/$DDUSER/deepdive

# db variables
export DBHOST=$PGHOST
export GPHOST=$PGHOST
export DBPORT=$PGPORT
export PGUSER=$DBUSER
export PGPASSWORD=${PGPASSWORD:-}

# ***** GREENPLUM VARS *****
export GPPATH=/lfs/local/0/$DDUSER/data/gp_data
export PATH=/lfs/local/0/senwu/software/greenplum/greenplum-db/bin:$PATH
source /lfs/local/0/senwu/software/greenplum/greenplum-db/greenplum_path.sh

# Using ddlib, analysis util lib
PYTHONPATH=$DEEPDIVE_HOME/ddlib:$DEEPDIVE_HOME/ddlib/ddlib:$REAL_DIRNAME/analysis/util:$PYTHONPATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$DEEPDIVE_HOME/lib/dw_linux/lib:$DEEPDIVE_HOME/lib/dw_linux/lib64
PATH=$PATH:$DEEPDIVE_HOME/ddlib
PATH=$PATH:$DEEPDIVE_HOME/sbt

# Switch to python3
unset PYTHONPATH
unset PYTHONHOME
export PATH=/lfs/local/0/senwu/software/python3/bin:$PATH
export PYTHONPATH="$PYTHONPATH:/lfs/local/0/senwu/software/"

