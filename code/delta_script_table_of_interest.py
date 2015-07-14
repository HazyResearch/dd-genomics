#! /usr/bin/env python

import config
from subprocess import call
import os
import sys

dduser = os.environ['DDUSER']
dbhost = os.environ['DBHOST']
dbport = os.environ['DBPORT']
dbname = os.environ['DBNAME']
app_home = os.environ['APP_HOME']
subsetFile = config.DELTA_IMPROVEMENT[sys.argv[1]]

call(['cp', app_home + '/code/deltaSubsets/' + sys.argv[1] + '/' + subsetFile, app_home + '/code/deltaSubsets/' + sys.argv[1] + '/main.sql'])
