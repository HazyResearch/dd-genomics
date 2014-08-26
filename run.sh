#! /bin/bash

DIRNAME=`dirname $0`
REAL_DIRNAME=`readlink -f ${DIRNAME}`

. "${REAL_DIRNAME}/env.sh"

cd $DEEPDIVE_HOME
### Run with deepdive binary:
#./deepdive -c $APP_HOME/application.conf
### Compile and run:
sbt/sbt "run -c $APP_HOME/application.conf"
