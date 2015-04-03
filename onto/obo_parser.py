#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A constant-space parser for the GeneOntology OBO v1.2 format

Version 1.0
"""
from collections import defaultdict

__author__    = "Uli Koehler"
__copyright__ = "Copyright 2013 Uli Koehler"
__license__   = "Apache v2.0"

def processGOTerm(goTerm):
    """
    In an object representing a GO term, replace single-element lists with
    their only member.
    Returns the modified object as a dictionary.
    """
    ret = dict(goTerm) #Input is a defaultdict, might express unexpected behaviour
    # for key, value in ret.iteritems():
    #     if len(value) == 1:
    #         ret[key] = value[0]
    return ret

def parseGOOBO(filename):
    """
    Parses a Gene Ontology dump in OBO v1.2 format.
    Yields each 
    Keyword arguments:
        filename: The filename to read
    """
    with open(filename, "r") as infile:
        currentGOTerm = None
        for line in infile:
            line = line.strip()
            if not line: continue #Skip empty
            if line == "[Term]":
                if currentGOTerm: yield processGOTerm(currentGOTerm)
                currentGOTerm = defaultdict(list)
            elif line == "[Typedef]":
                #Skip [Typedef sections]
                currentGOTerm = None
            else: #Not [Term]
                #Only process if we're inside a [Term] environment
                if currentGOTerm is None: continue
                key, sep, val = line.partition(":")
                currentGOTerm[key].append(val.strip())
        #Add last term
        if currentGOTerm is not None:
            yield processGOTerm(currentGOTerm)

if __name__ == "__main__":
    """Print out the number of GO objects in the given GO OBO file"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='The input file in GO OBO v1.2 format.')
    args = parser.parse_args()
    #Iterate over GO terms
    termCounter = 0
    for goTerm in parseGOOBO(args.infile):
        termCounter += 1
    print "Found %d GO terms" % termCounter