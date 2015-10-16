#! /usr/bin/env python

import sys
import glob
import os

if __name__ == "__main__":
  num = 0
  if len(sys.argv) != 2:
    print >>sys.stderr, 'Expecting list of folder names (without preceding numbers) in file as argument'
    sys.exit(1)
  with open(sys.argv[1]) as f:
    for line in f:
      assert num <= 99, 'Cannot handle more than 100 files (indices 00-99)'
      filenames = glob.glob(line.strip())
      assert len(filenames) <= 1, 'Multiple files of name %s' % line.strip()
      if filenames:
        filename = filenames[0]
        stem = filename
      else:
        filenames = glob.glob('[0-9][0-9]-%s' % line.strip())
        assert len(filenames) == 1, 'No file with name *-%s' % line.strip()
        filename = filenames[0]
        stem = filenames[0][3:]
      new_filename = '%02d-%s' % (num, stem)
      if new_filename != filename:
        print 'Moving %s to %s' % (filename, new_filename)
        os.rename(filename, new_filename)
      else:
        print 'Retaining filename %s' % filename
      num += 1

