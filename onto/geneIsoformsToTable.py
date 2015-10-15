#! /usr/bin/env python

import sys

def main():
  fname = sys.argv[1]
  transcript = None
  with open(fname) as f:
    for line in f:
      if line.startswith('>'):
        if transcript:
          print '%s\t{%s}' % (transcript, ','.join(sequence)) 
        transcript = line.strip()[1:].split()[0].split('_')[2]
        sequence = ''
        continue
      sequence += line.strip()
  print '%s\t{%s}' % (transcript, ','.join(sequence)) 

if __name__ == "__main__":
  main()
