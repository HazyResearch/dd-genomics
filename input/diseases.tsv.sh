#! /bin/bash

if [ -z $GDD_HOME ]
then
  echo "Set GDD_HOME!!" >> /dev/stderr
  exit 1
fi

save=$PWD
cd $GDD_HOME/onto
./create_allowed_diseases.sh
cd $save

cat $GDD_HOME/onto/manual/diseases.tsv | $GDD_HOME/code/create_allowed_diseases_list.py
