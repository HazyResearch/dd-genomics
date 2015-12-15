#! /usr/bin/env python

import sys

def rc_to_mc(mixin, sent, cands, node, children, rv=[]):
  mc = MatchCell(1)
  rv.append(mc)
  index = len(rv)
  for i, cand in enumerate(cands):
    if node == cand:
      mc.cands = [i]
      break
  mc.lemmas = [mixin.get_lemma(sent, node)]
  mc.words = [mixin.get_word(sent, node)]
  mc.match_type = 'single_match'
  mc.pos_tags = [mixin.get_pos_tag(sent, node)]
  for c in children[node]:
    if c == 0:
      continue
    c_index, _ = rc_to_mc(mixin, sent, cands, c, children, rv)
    mc.children.append(c_index)
  if not mc.children:
    mc.children.append(0)
  return index, rv

def sent_to_mc(sent, cands):
  m = AlignmentMixin()
  root = m.find_root(sent['dependencies'])
  children = m.find_children(sent)
  return rc_to_mc(m, sent, cands, root, children)

class OverlappingCandidatesException(Exception):
  pass

def canonicalize_row(words, lemmas, poses, dep_paths, dep_parents, cands):
  for i, cand_series1 in enumerate(cands):
    for j, cand_series2 in enumerate(cands):
      if i == j:
        continue
      if len(set(cand_series1).intersection(set(cand_series2))) != 0:
        raise OverlappingCandidatesException

  new_indices = [i for i in xrange(len(words))]
  new_words = [None for _ in xrange(len(words))]
  new_lemmas = [None for _ in xrange(len(words))]
  new_poses = [None for _ in xrange(len(words))]
  new_cands = []
  for cand_series in cands:
    first_cand_index = new_indices[cand_series[0]]
    offset = len(cand_series) - 1
    for i in cand_series:
      new_indices[i] = first_cand_index
    for i in xrange(max(cand_series)+1, len(new_indices)):
      new_indices[i] -= offset
    cand_series = sorted(list(cand_series))
    cand_word_series = [words[i] for i in cand_series]
    cand_word = '_'.join(cand_word_series)
    new_words[first_cand_index] = cand_word
    new_lemmas[first_cand_index] = cand_word.lower()
    new_poses[first_cand_index] = 'NN'
    new_cands.append(first_cand_index)
  
  all_cand_words = set([i for cand_series in cands for i in cand_series])
  for i in xrange(len(words)):
    if new_indices[i] in new_cands:
      continue
    new_words[new_indices[i]] = words[i]
    new_lemmas[new_indices[i]] = lemmas[i]
    new_poses[new_indices[i]] = poses[i]
  
  new_words = [w for w in new_words if w is not None]
  new_lemmas = [l for l in new_lemmas if l is not None]
  new_poses = [p for p in new_poses if p is not None]
    
  new_dep_parents_paths = [set() for _ in xrange(len(new_words))]
  for i, parent in enumerate(dep_parents):
    if new_indices[i] == new_indices[parent]:
      # within candidate
      pass
    else:
      new_dep_parents_paths[new_indices[i]].add((new_indices[parent], dep_paths[i]))
  
  new_dep_parents = []
  new_dep_paths = []
  for parent_paths in new_dep_parents_paths:
    no_minus_one_paths = [p for p in parent_paths if p[0] != -1]
    if len(no_minus_one_paths) > 0:
      new_dep_parents.append([p[0] for p in no_minus_one_paths])
      new_dep_paths.append([p[1] for p in no_minus_one_paths])
    else:
      new_dep_parents.append([-1])
      new_dep_paths.append([''])
  return new_words, new_lemmas, new_poses, new_dep_paths, new_dep_parents, new_cands

def parts_to_mc(words, lemmas, poses, children, node, cands, rv=[]):
  mc = MatchCell(1)
  rv.append(mc)
  index = len(rv)
  for i, cand in enumerate(cands):
    if node == cand:
      mc.cands = [i]
      break
  mc.lemmas = [lemmas[node-1]]
  mc.words = [words[node-1]]
  mc.match_type = 'single_match'
  mc.pos_tags = [poses[node-1]]
  for c in children[node]:
    if c == 0:
      continue
    c_index, _ = parts_to_mc(words, lemmas, poses, children, c, cands, rv)
    mc.children.append(c_index)
  if not mc.children:
    mc.children.append(0)
  return index, rv

def parents_to_children(dep_parents):
  children = [[] for _ in xrange(len(dep_parents) + 1)]
  for node, parents in enumerate(dep_parents):
    for p in parents:
      if p != -1:
        assert p+1 < len(children), (p, len(children), dep_parents)
        children[p+1].append(node+1)
  for i, c in enumerate(children):
    if i == 0:
      continue
    if not c:
      c.append(0)
  return children

class RootException(Exception):
  pass

def parents_find_root(dep_parents):
  roots = []
  for i, parents in enumerate(dep_parents):
    if parents != [-1]:
      continue
    if not [p for p in dep_parents if (i in p)]:
      continue
    roots.append(i+1)
  if len(roots) != 1:
    raise RootException("have != 1 roots (%s) in sentence" % str(roots))
  return roots[0]

class DepParentsCycleException(Exception):
  pass

def incoming(node, children):
  rv = []
  for i, c in enumerate(children):
    if node in c:
      rv.append(i)
  return rv

def acyclic(children):
  children = [set(c) for c in children]
  l = []
  q = []
  for node in xrange(len(children)):
    if not incoming(node, children):
      q.append(node)
  while q:
    n = q[0]
    q = q[1:]
    l.append(n)
    for m in children[n]:
      incom = incoming(m, children)
      if incom == [n]:
        q.append(m)
    children[n].clear()
  
  for c in children:
    if c:
      return False
  return True

def row_to_canonical_mc(row, in_cands):
  words, lemmas, poses, dep_paths, dep_parents = row.words, row.lemmas, row.poses, row.dep_paths, row.dep_parents
  words, lemmas, poses, dep_paths, dep_parents, cands = canonicalize_row(words, lemmas, poses, dep_paths, dep_parents, in_cands)
  # we are converting from 0 to 1-based now
  cands = [c+1 for c in cands]
  children = parents_to_children(dep_parents) # takes 0-based, returns 1-based
  if not acyclic(children):
    raise DepParentsCycleException()
  root = parents_find_root(dep_parents) # takes 0-based, returns 1-based
  return parts_to_mc(words, lemmas, poses, children, root, cands)

class MatchCell:

  def __init__(self, size):
    self.size = size

    self.match_type = [None for _ in xrange(size)]
    self.pos_tags = [None for _ in xrange(size)]
    self.words = [None for _ in xrange(size)]
    self.lemmas = [None for _ in xrange(size)]
    self.cands = [None for _ in xrange(size)]
    self.children = []
  
  def __repr__(self):
    return '[%s,%s,%s,%s,%s,%s,%s]' % (str(self.size), \
                                      str(self.match_type), \
                                      str(self.pos_tags), \
                                      str(self.words), \
                                      str(self.lemmas), \
                                      str(self.cands), \
                                      str(self.children))

class AlignmentMixin:

  def find_root(self, dep):
    for d in dep:
      if d[1].lower() == "root-0":
        d2split = d[2].split('-')
        return int(d2split[len(d2split) - 1])
    assert False

  def find_children(self, sent):
    dep = sent['dependencies']
    rv = [ set() for i in xrange(len(sent['words']) + 1)]
    for d in dep:
      d1split = d[1].split('-')
      from_index = int(d1split[len(d1split) - 1])
      d2split = d[2].split('-')
      to_index = int(d2split[len(d2split) - 1])
      rv[from_index].add(to_index)
      assert to_index <= len(sent['words'])
    for i, c in enumerate(rv):
      if len(c) == 0:
        rv[i].add(0)
    return rv

  def in_dicts(self, w1, w2, dicts):
    for d in dicts:
      if w1 in d and w2 in d:
        return True
    return False
  
  def get_word(self, sent, node):
    return sent['words'][node - 1][0]
  
  def get_lemma(self, sent, node): 
      return sent['words'][node - 1][1]["Lemma"]
    
  def get_pos_tag(self, sent, node):
    # HACK Johannes: take only first letter of POS tag for matching
    return sent['words'][node - 1][1]["PartOfSpeech"][0]