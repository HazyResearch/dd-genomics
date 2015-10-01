#! /bin/bash

if [ $# -ne 1 ]
then
  echo "usage: $0 backup_files.txt" >> /dev/stderr
  exit 1
fi

backup_files=$1

backup_dir=`head -n 1 $backup_files`
while true
do
  echo "backing up"
  newdir=${backup_dir}/`date +'%Y-%m-%d-%H-%M-%S'`
  mkdir -p $newdir
  echo $newdir
  for instr in `tail -n+2 $backup_files`
  do
    f=`echo $instr | cut -d ';' -f 1`
    name=`echo $instr | cut -d ';' -f 2`
    echo "$f $name"
    cp $f $newdir/$name
  done
  sleep 120
done
