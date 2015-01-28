#!/usr/bin/env python
# A script for seeing basic statistics about the number and type of gene mentions extracted
# Author: Alex Ratner <ajratner@stanford.edu>
# Created: 2015-01-25
import sys
from dd_analysis_utils import process_pg_statistics

if __name__ == '__main__':
  if len(sys.argv) < 3:
    print "Process.py: Insufficient arguments"
  else:
    process_pg_statistics(sys.argv[1], sys.argv[2])
