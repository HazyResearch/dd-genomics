#! /bin/bash

# TODO: Specify these variables according to your system configuration!
# the user running the application
export DDUSER=
# the database user (default: the same as above) & connection vars
export DBUSER=$DDUSER
export DBHOST=
export DBPORT=
export DBNAME=
# the port that gpfdist will run on (should be uique for each user on system!)
export GPPORT=

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
export PGUSER=$DBUSER
export GPUSER=$DBUSER
export PGHOST=$DBHOST
export GPHOST=$DBHOST
export PGPORT=$DBPORT
export PGPASSWORD=${PGPASSWORD:-}

# ***** GREENPLUM VARS *****
#source /lfs/local/0/senwu/software/greenplum/greenplum-db/greenplum_path.sh
export GPPATH=/lfs/local/0/$DDUSER/data/gp_data
export GPHOME=/lfs/local/0/senwu/software/greenplum/greenplum-db
export PATH=$GPHOME/bin:$PATH
#export PATH=$GPHOME/ext/python/bin:$PATH
export LD_LIBRARY_PATH=$GPHOME/lib:$GPHOME/ext/python/lib:$LD_LIBRARY_PATH
export OPENSSL_CONF=$GPHOME/etc/openssl.cnf

# Using ddlib, analysis util lib
export PYTHONPATH=$PYTHONPATH:$DEEPDIVE_HOME/ddlib:$DEEPDIVE_HOME/ddlib/ddlib:$REAL_DIRNAME/analysis/util
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$DEEPDIVE_HOME/lib/dw_linux/lib:$DEEPDIVE_HOME/lib/dw_linux/lib64
export PATH=$PATH:$DEEPDIVE_HOME/ddlib:$DEEPDIVE_HOME/sbt

# Switch to python3
#unset PYTHONPATH
#unset PYTHONHOME
#export PATH=/lfs/local/0/senwu/software/python3/bin:$PATH
#export PYTHONPATH="$PYTHONPATH:/lfs/local/0/senwu/software/"
