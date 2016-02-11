#! /usr/bin/env python

import sys

if len(sys.argv) != 4:
  print >> sys.stderr, "usage: ./blah diseases_file ps_file ps_to_omim_file"
  sys.exit(1)

diseases_filename = sys.argv[1]
ps_filename = sys.argv[2]
ps_to_omim_filename = sys.argv[3]

omim_to_ps = {}

ps_alt_names = {}

with open(ps_to_omim_filename) as f:
  for line in f:
    line = line.strip().split('\t')
    omim_to_ps[line[1]] = line[0]

omim_names = {}
omim_alt_names = {}

with open(diseases_filename) as f:
  for line in f:
    line = line.strip().split('\t')
    omim_id = line[0]
    names = line[1]
    if len(line) >= 3:
      alt_names = line[2]
    else:
      alt_names = ''
    omim_names[omim_id] = names
    if omim_id in omim_to_ps:
      omim_alt_names[omim_id] = ''
      ps_id = omim_to_ps[omim_id]
      if ps_id not in ps_alt_names:
        ps_alt_names[ps_id] = []
      if len(alt_names) > 0:
        ps_alt_names[ps_id].extend(alt_names.split('|^|'))
    else:
      omim_alt_names[omim_id] = alt_names

ps_names = {}

with open(ps_filename) as f:
  for line in f:
    line = line.strip().split('\t')
    ps_names[line[0]] = line[1]

with open(diseases_filename, 'w') as f:
  f.seek(0)
  for omim_id in omim_names:
    names = omim_names[omim_id]
    alt_names = omim_alt_names[omim_id]
    if alt_names is not None:
      print >> f, "%s\t%s\t%s" % (omim_id, names, alt_names)
    else:
      print >> f, "%s\t%s\t" % (omim_id, names)

with open(ps_filename, 'w') as f:
  f.seek(0)
  for ps_id in ps_names:
    name = ps_names[ps_id]
    if ps_id in ps_alt_names:
      alt_names = '|^|'.join(ps_alt_names[ps_id])
    else:
      alt_names = ''
    print >> f, "%s\t%s\t%s" % (ps_id, name, alt_names)

