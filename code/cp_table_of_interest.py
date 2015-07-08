#! /usr/bin/env python

import config
from subprocess import call
import os

if __name__ == "__main__":
  print "Hello"
  dduser = os.environ['DDUSER']
  dbhost = os.environ['DBHOST']
  dbport = os.environ['DBPORT']
  dbname = os.environ['DBNAME']
  app_home = os.environ['APP_HOME']
  subsetFile = config.DELTA_IMPROVEMENT['subset']

  call(['cp', app_home + '/code/deltaSubsets/' + subsetFile, app_home + '/code/deltaSubsets/main.sql'])

