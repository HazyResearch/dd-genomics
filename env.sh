#! /bin/bash

DIRNAME=`dirname $0`
REAL_DIRNAME=`readlink -f ${DIRNAME}`

export DEEPDIVE_HOME=`cd ${REAL_DIRNAME}/../..; pwd`
export APP_HOME=`pwd`

# Machine Configuration
export MEMORY="32g"
export PARALLELISM=4

# Database Configuration
export DBNAME=genomics
export PGUSER=${PGUSER:-`whoami`}
export PGPASSWORD=${PGPASSWORD:-}
export PGPORT=${PGPORT:-5432}
export PGHOST=${PGHOST:-localhost}

# SBT Options
export SBT_OPTS="-Xmx$MEMORY"
export JAVA_OPTS="-Xmx$MEMORY"

# Using ddlib
export PYTHONPATH=$DEEPDIVE_HOME/ddlib:$PYTHONPATH

