#!/usr/bin/env python
# A script for seeing basic statistics about the number and type of gene mentions extracted
# Author: Alex Ratner <ajratner@stanford.edu>
# Created: 2015-01-25
import sys
import csv
import re

# Kinds of statistics tracked automatically by postgres "ANALYZE" command
# https://github.com/postgres/postgres/blob/master/src/include/catalog/pg_statistic.h
STAT_KINDS = {
  1: 'most_common_values',
  2: 'histogram',
  3: 'correlation_to_row_order',
  4: 'most_common_elements',
  5: 'distinct_elements_count_histogram',
  6: 'range_length_histogram',
  7: 'bounds_histogram'}

def unnest(row):
  return re.split(r'\"*,\"*', re.sub(r'^\"*\{\"*|\"*\}\"*$', '', row))

def process_pg_statistics(path_to_data, root_path_out):
  with open(path_to_data, 'rb') as csvf:
    csv_reader = csv.reader(csvf)
    NUM_STATS = 0
    STA_START = 0
    for i,row in enumerate(csv_reader):
      
      # figure out how many different statistics are contained in the table
      if i == 0:
        for j,cell in enumerate(row):
          cell_match = re.match(r'stakind(\d+)', cell)
          if cell_match is not None:
            NUM_STATS = int(cell_match.group(1))
            if NUM_STATS == 1:
              STA_START = j
        continue

      # get the column this row is referring to
      col = int(row[1])

      # for each row, unpack each seperate statistic and output to file
      for s in range(NUM_STATS):

        # for each of the rows, identify which type of statistic
        stat_kind = int(row[STA_START + s])
        if STAT_KINDS.has_key(stat_kind):
          stat_label = STAT_KINDS[stat_kind]
        elif stat_kind == 0:
          continue
        else:
          stat_label = "Other_%s" % (stat_kind,)

        # unpack and zip value / stat lists
        vals = unnest(row[STA_START+(3*NUM_STATS)+s])
        stats = unnest(row[STA_START+(2*NUM_STATS)+s])
        data = zip(vals, stats)
        if len(data) < 2:
          continue

        # output as csv file
        with open("%s_%s_%s.csv" % (root_path_out, col, stat_label), 'wb') as data_out:
          csv_writer = csv.writer(data_out)
          for d in data:
            csv_writer.writerow(d)

if __name__ == '__main__':
  if len(sys.argv) < 3:
    print "Process.py: Insufficient arguments"
  else:
    process_pg_statistics(sys.argv[1], sys.argv[2])
