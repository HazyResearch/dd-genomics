#!/usr/bin/env python
# Author: Alex Ratner <ajratner@stanford.edu>
# Created: 2015-01-25
import sys
import os
import csv
from collections import defaultdict

# there is 1 group_by col + 1 total_count + 1 labeled_true + 1 labeled_false + 10 bucket_n
N_COLS = 14

if __name__ == '__main__':
  if len(sys.argv) < 4:
    print "Process.py: Insufficient arguments"
  else:

    # get the correct dict
    if sys.argv[3] == 'gene_mentions':
      dict_name = 'merged_genes_dict'
    elif sys.argv[3] == 'pheno_mentions' or sys.argv[3] == 'hpoterm_mentions':
      dict_name = 'hpo_terms'
    else:
      dict_name = None 
    if dict_name is not None:

      # load the data & mark seen entities
      data = []
      seen = defaultdict(lambda: None)
      with open(sys.argv[1], 'rb') as f_in:
        csv_reader = csv.reader(f_in)
        for row in csv_reader:
          data.append(row)
          seen[row[0]] = True

      # load the dict & append zero values to data for unseen entities
      # NOTE: assume entity names in col 0
      DICT_PATH = "%s/dicts/%s.tsv" % (os.environ['GDD_HOME'], dict_name)
      with open(DICT_PATH, 'rb') as f_in:
        tsv_reader = csv.reader(f_in, delimiter='\t')
        for row in tsv_reader:
          if seen[row[0]] is None:
            data.append([row[0]] + [0]*(N_COLS-1))

      # output the appended data
      with open("%s_appended.csv" % (sys.argv[2],), 'wb') as f_out:
        csv_writer = csv.writer(f_out)
        for row in data:
          csv_writer.writerow(row)
