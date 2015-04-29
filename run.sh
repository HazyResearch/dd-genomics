#! /bin/bash

export JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF-8

if [ -f env_local.sh ]; then
  echo "Using env_local.sh"
  source ./env_local.sh
else
  echo "Using env.sh"
  source ./env.sh
fi


if [ -f $DEEPDIVE_HOME/sbt/sbt ]; then
  echo "DeepDive $DEEPDIVE_HOME"
else
  echo "[ERROR] Could not find sbt in $DEEPDIVE_HOME!"
  exit 1
fi

unset GDD_PIPELINE
if [ "${1-}" == "" ]; then
  echo "Usage: ./run.sh [PIPELINE_TO_RUN]"
  exit 1
else
  export GDD_PIPELINE="$1"
fi

cd $DEEPDIVE_HOME
sbt "run -c $APP_HOME/${APP_CONF:-application.conf}"
