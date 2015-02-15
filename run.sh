#! /bin/bash

export JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF-8

source ./env.sh

if [ -f $DEEPDIVE_HOME/sbt/sbt ]; then
  echo "DeepDive $DEEPDIVE_HOME"
else
  echo "[ERROR] Could not find sbt in $DEEPDIVE_HOME!"
  exit 1
fi

cd $DEEPDIVE_HOME
sbt "run -c $APP_HOME/application.conf"
