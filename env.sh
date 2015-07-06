#! /bin/bash

# TODO: Specify these variables according to your system configuration!
# the user running the application
export DDUSER=${DD_APPUSER-$(whoami)}
# the database user (default: the same as above) & connection vars
export DBUSER=${DD_DBUSER-${PGUSER-${DDUSER}}}
export DBHOST=${DD_DBHOST-${PGHOST}}
export DBPORT=${DD_DBPORT-${PGPORT-5432}}
export DBNAME=${DD_DBNAME-}
# the port that gpfdist will run on (should be uique for each user on system!)
export GPPORT=
# the type of postgres being used: "pg" for postgres | "gp" for greenplum
export DBTYPE=

# TODO: Set dir for preprocessing
export BAZAAR_DIR=

# TODO: python packages (in long term get rid of stuff like this; in short term keep minimal)
export PYTHONPATH=$PYTHONPATH:/lfs/local/0/ajratner/packages/lib/python2.7/site-packages

# TODO: Machine Configuration
export MEMORY="256g"
export PARALLEL_GROUNDING="${DD_PARALLEL_GROUNDING-true}"
export PARALLELISM=80
export SBT_OPTS="-Xmx$MEMORY"
export JAVA_OPTS="-Xmx$MEMORY"

# Directory variables
# NOTE: if using mac, need to install coreutils / greadlink, or hardcode here...
DIRNAME=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
REAL_DIRNAME=`readlink -f ${DIRNAME}` || REAL_DIRNAME=`greadlink -f ${DIRNAME}`
export APP_HOME=$REAL_DIRNAME
export GDD_HOME=$APP_HOME
export DEEPDIVE_HOME=${DEEPDIVE_HOME-/lfs/local/0/$DDUSER/deepdive}

# db variables
export PGUSER=$DBUSER
export GPUSER=$DBUSER
export PGHOST=$DBHOST
export GPHOST=$DBHOST
export PGPORT=$DBPORT
export PGPASSWORD=${PGPASSWORD:-}

# ***** GREENPLUM VARS *****
export GPPATH=/lfs/local/0/$DDUSER/data/gp_data
export GPHOME=/lfs/local/0/senwu/software/greenplum/greenplum-db
export OPENSSL_CONF=$GPHOME/etc/openssl.cnf

# Using ddlib, analysis util lib
export PYTHONPATH=$PYTHONPATH:$DEEPDIVE_HOME/ddlib:$DEEPDIVE_HOME/ddlib/ddlib:$REAL_DIRNAME/analysis/util
export LD_LIBRARY_PATH=$DEEPDIVE_HOME/lib/dw_linux/lib:$DEEPDIVE_HOME/lib/dw_linux/lib64:$LD_LIBRARY_PATH
export PATH=$PATH:$DEEPDIVE_HOME/ddlib:$DEEPDIVE_HOME/sbt
