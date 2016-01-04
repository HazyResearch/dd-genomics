#! /usr/bin/python -m trace --trace --file /dev/stderr

######################################################################################
#  LATTICE - Util functions for working with dependencies
#
#  Usage:
#    Start by preparing a list of dep_patterns, eg. "he <-nsubj- buy"
#
#    sentence is an object that contains dep_paths, dep_parents, lemmas.
#
#    parents, children = build_indexes(sentence)
#    matches = []
#
#    for p in dep_patterns:
#        match(sentence, p, parents, children, matches)
#
#    Each m in in maches is a list of the word ids that matched the pattern.
#
######################################################################################

import sys
import re

def build_indexes(sentence):
    l = len(sentence['dep_paths'])
    parents = [] 
    children = []
    for i in range(0, l):
        parents.append([])
        children.append([])
    for i in range(0, l):        
        p = sentence['dep_parents'][i]
        t = sentence['dep_paths'][i]
        children[p].append([t, i])
        parents[i].append([t, p])
    return [parents, children]

def match(sentence, path_arr, mention_parts, parents, children, dicts = {}):
    matches = []
    for i in range(0, len(sentence['words'])):
        match_i(sentence, i, path_arr, mention_parts, parents, children, matches, [], dicts)
    return matches

def token_match(sentence, i, pw, mention_parts, dicts):
    #w = sentence['words'][i].lower()
    w = sentence['lemmas'][i].lower()
    t = pw.split('|')
    #print(dicts, file=sys.stderr)
    #print('.... checking ' + pw)
    for s in t:
        pair = s.split(':')
        p = re.compile('cand\[(\d)\]')
        m = p.match(pair[0])
        if m:
            cand_num = int(m.group(1))
            cand_wordidxs = mention_parts[cand_num]
            if i in cand_wordidxs:
                return True
        elif pair[0] == 'dic':
            if not pair[1] in dicts:
                print >>sys.stderr, 'ERROR: Dictionary ' + pair[1] + ' not found'
                return False
            if not w in dicts[pair[1]]:
                return False
        elif pair[0] == 'pos':
            if not pair[1] == sentence['poses'][i]:
                return False
        elif pair[0] == 'reg':
            if not re.match(pair[1], w):
                return False
        else:
            print >>sys.stderr, 'ERROR: Predicate ' + pair[0] + ' unknown'
            return False
    return True 
      

def match_i(sentence, i, path_arr, mention_parts, parents, children, matches, matched_prefix = [], dicts = {}):
    assert len(path_arr) > 0, str(path_arr)
    #w = sentence['lemmas'][i].lower()
    #if len(path_arr) == 0:
        # nothing to match anymore
        #matches.append(matched_prefix)
        #return True

    pw = path_arr[0]
    # __ is a wildcard matching every word
    
    matched = False
    if pw == '__':
        matched = True
    elif pw.startswith('[') and pw.endswith(']') and token_match(sentence, i, pw[1:-1], mention_parts, dicts):
        matched = True
    elif sentence['lemmas'][i].lower() == pw:
        matched = True

    if not matched:
        return False

    #if pw != '__' and w != pw:
    #    return

    matched_prefix.append(i)
    if len(path_arr) == 1:
        matches.append(matched_prefix)
        return True

    # match dep
    pd = path_arr[1]
    found = False
    if pd[:2] == '<-':
        # left is child
        dep_type = pd[2:-1]
        for p in parents[i]:
            #print(w + '\t<-' + p[0] + '-\t' + str(p[1]) + '\t' + sentence.words[p[1]].lemma, file=sys.stderr) 
            if p[0] == dep_type or dep_type == '__':
                if match_i(sentence, p[1], path_arr[2:], mention_parts, parents, children, matches, list(matched_prefix), dicts):
                    found = True
    elif pd[len(pd)-2:] == '->':
        # left is parent
        dep_type = pd[1:-2]
        for c in children[i]:
            #print(w + '\t-' + c[0] + '->\t' + str(c[1]) + '\t' + sentence.words[c[1]].lemma, file=sys.stderr) 
            if c[0] == dep_type or dep_type == '__':
                if match_i(sentence, c[1], path_arr[2:], mention_parts, parents, children, matches, list(matched_prefix), dicts):
                    found = True
    elif pd == '_':
        if i+1 < len(sentence['lemmas']):
            if match_i(sentence, i+1, path_arr[2:], mention_parts, parents, children, matches, list(matched_prefix), dicts):
                found = True
    
    return found
    
def enclosing_range(wordidxs):
    m = wordidxs
    if len(m) == 1:
        m_from = m[0]
        m_to = m[0] + 1
    else:
        if m[0] < m[1]:
            m_from = m[0]
            m_to = m[len(m)-1] + 1
        else:
            m_from = m[len(m)-1]
            m_to = m[0]+1
    return [ m_from, m_to ]

