#! /usr/bin/env python

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