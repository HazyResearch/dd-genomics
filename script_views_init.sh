#!/bin/sh

while true; do
    read -p "Have you checked deepdive and mindbender are correctly installed ?" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) echo 'In your deepdive folder, you can run the following commands'; 
				echo 'git pull';
				echo 'git checkout master';
				echo 'git pull';
				echo 'git submodule update --init';
				echo 'make';
				echo 'make install #PREFIX=...';
				echo 'cd util/mindbender';
				echo 'git submodule update --init';
				echo 'cd ../..';
				echo 'make build-mindbender install #PREFIX=/lfs/raiders7/0/tpalo/local';
				exit;;
        * ) echo "Please answer y or n.";;
    esac
done
echo 

#Make sure deepdive and mindbender is correctly installed

# #In deepdive home


if [ "$#" -ne 1 ] ; then
  echo "Usage: $0 name_database_for_views" >&2
  exit 1
fi


#To be run in your original dd-genomics folder
if [[ ! ( -d ${1}_for_views) ]]
then
  git clone git@github.com:HazyResearch/dd-genomics.git ../${1}_for_views
  rm -rf ../${1}_for_views/onto
  cp -r onto ../{1}_for_views
fi
cd ../${1}_for_views
git checkout thomas-improving-views
# git pull
# git fetch
# git pull
echo "postgresql://localhost:5432/$1" > db.url
deepdive compile
deepdive do init/db
