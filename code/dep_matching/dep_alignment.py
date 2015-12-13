#! /usr/bin/env python

import sys

sys.path.append('/Users/jbirgmei/Stanford/Bejerano/stanford-corenlp-python')

import jsonrpc
from simplejson import loads
import numpy as np
from sw_util import AlignmentMixin, MatchCell

class DepAlignment(AlignmentMixin):

  score_matrix = None
  path_matrix = None
  sent1 = None
  sent2 = None
  dep1 = None
  dep2 = None
  root1 = None
  root2 = None
  children1 = None
  children2 = None

  word_match_score = 5
  dict_match_score = 5
  lemma_match_score = 5
  pos_tag_match_score = 1
  skip_score = -3
  mismatch_score = -5
  cand_match_score = 15

  def __init__(self, sent1, sent2, cands1, cands2, dicts):
    self.sent1 = sent1
    self.sent2 = sent2
    self.dicts = dicts
    self.dep1 = self.sent1['dependencies']
    self.dep2 = self.sent2['dependencies']
    self.cands1 = cands1
    self.cands2 = cands2
    assert len(cands1) == len(cands2)

    self.score_matrix = np.empty((len(self.sent1['words'])+1, len(self.sent2['words'])+1))
    self.score_matrix[:] = np.inf
    self.path_matrix = [[('_', 0) for i in xrange(len(self.sent2['words']) + 1)] for j in xrange(len(self.sent1['words']) + 1)]
    for d in dicts:
      assert isinstance(d, set)

    self.root1 = self.find_root(self.dep1)
    self.root2 = self.find_root(self.dep2)
    self.children1 = self.find_children(self.sent1)
    self.children2 = self.find_children(self.sent2)

    self._h(self.root1, self.root2)

  def _match_score(self, node1, node2):
    word1 = self.get_word(self.sent1, node1)
    word2 = self.get_word(self.sent2, node2)
    lemma1 = self.get_lemma(self.sent1, node1)
    lemma2 = self.get_lemma(self.sent2, node2)
    pos_tag1 = self.get_pos_tag(self.sent1, node1)
    pos_tag2 = self.get_pos_tag(self.sent2, node2)

    for i in xrange(len(self.cands1)):
      if node1 == self.cands1[i] and node2 == self.cands2[i]:
        return self.cand_match_score, 'cand_%d_match' % i
    if pos_tag1 == pos_tag2 and word1 == word2:
      return self.word_match_score, 'direct_word_match'
    if pos_tag1 == pos_tag2 and lemma1 == lemma2:
      return self.lemma_match_score, 'direct_lemma_match'
    if self.in_dicts(word1, word2, self.dicts):
      return self.dict_match_score, 'word_dict_match'
    if self.in_dicts(lemma1, lemma2, self.dicts):
      return self.dict_match_score, 'lemma_dict_match'
    if pos_tag1 == pos_tag2:
      return self.pos_tag_match_score, 'pos_tags_match'
    return self.mismatch_score, 'mismatch'
  
  def _match(self, node1, node2):
    if node1 == 0 and node2 == 0:
      return 0, 'end', []
    if node1 == 0 and node2 != 0:
      return -1000, 'assert_false', []
    if node1 != 0 and node2 == 0:
      return -1000, 'assert_false', []
    score_list = []
  
    c1 = set(self.children1[node1])
    assert node1 not in c1, (node1, c1)
    c2 = set(self.children2[node2])
    assert node2 not in c2, (node1, c2)
  
    for i in c1:
      for j in c2:
        self._h(i, j)
        score_list.append((self.score_matrix[i, j], i, j))
    score_list = sorted(score_list)[::-1]
  
    outgoing = []
    sum_score = 0
    while c1 or c2:
      head_score = score_list[0]
      score_list = score_list[1:]
      x1 = head_score[1]
      x2 = head_score[2]
      if x1 in c1 or x2 in c2:
        outgoing.append((x1, x2))
        c1 -= set([x1])
        c2 -= set([x2])
        sum_score += head_score[0]
    
    direct_match_score, direct_match_type = self._match_score(node1, node2)
    for o1, o2 in outgoing:
      assert node1 != o1
      assert node2 != o2

    return direct_match_score + sum_score, direct_match_type, outgoing
  
  def _skip1(self, node1, node2):
    if node1 == 0 and node2 == 0:
      return -1000, 'assert_false', []
    if node1 == 0 and node2 != 0:
      return -1000, 'assert_false', []
    score_list = []
  
    c1 = self.children1[node1]
    for i in c1:
      self._h(i, node2)
      score_list.append((self.score_matrix[i, node2], i))
    score_list = sorted(score_list)[::-1]
    
    assert score_list[0][1] != node1, str((score_list[0][1], node1))
    return self.skip_score + score_list[0][0], 'skip1', [(score_list[0][1], node2)]
  
  def _skip2(self, node1, node2):
    if node1 == 0 and node2 == 0:
      return -1000, 'assert_false', []
    if node1 != 0 and node2 == 0:
      return -1000, 'assert_false', []
    score_list = []
  
    c2 = self.children2[node2]
    for j in c2:
      assert j != node2
      self._h(node1, j)
      score_list.append((self.score_matrix[node1, j], j))
    score_list = sorted(score_list)[::-1]
    
    assert score_list[0][1] != node2, str((node2, score_list[0][1]))
    return self.skip_score + score_list[0][0], 'skip2', [(node1, score_list[0][1])]
  
  def _h(self, node1, node2):
    if self.score_matrix[node1, node2] != np.inf:
      return self.score_matrix[node1, node2]
  
    m, match_type, cont_match = self._match(node1, node2)
    assert node1 not in [c[0] for c in cont_match]
    assert node2 not in [c[1] for c in cont_match]
    l1, skip_type1, cont_skip1 = self._skip1(node1, node2)
    assert (node1, node2) not in cont_skip1
    l2, skip_type2, cont_skip2 = self._skip2(node1, node2)
    assert (node1, node2) not in cont_skip2
    
    score = max([m, l1, l2])
    
    self.score_matrix[node1, node2] = score
    if score == m:
      self.path_matrix[node1][node2] = match_type, cont_match
    elif score == l1:
      self.path_matrix[node1][node2] = skip_type1, cont_skip1
    elif score == l2:
      self.path_matrix[node1][node2] = skip_type2, cont_skip2
    else:
      assert False

  def get_match_tree(self, match_tree=[], node1=None, node2=None):
    if node1 == None:
      node1 = self.root1
    if node2 == None:
      node2 = self.root2

    mc = MatchCell(2)
    for i in xrange(len(self.cands1)):
      if node1 == self.cands1[i]:
        mc.cands[0] = i
      if node2 == self.cands2[i]:
        mc.cands[1] = i

    instr, succ = self.path_matrix[node1][node2]
      
    if instr == 'end':
      return None, None
    
    if instr.endswith('match'):
      mc.words[0] = self.get_word(self.sent1, node1)
      mc.words[1] = self.get_word(self.sent2, node2)
      mc.lemmas[0] = self.get_lemma(self.sent1, node1)
      mc.lemmas[1] = self.get_lemma(self.sent2, node2)
      mc.pos_tags[0] = self.get_pos_tag(self.sent1, node1)
      mc.pos_tags[1] = self.get_pos_tag(self.sent2, node2)
    elif instr == 'skip1':
      mc.words[0] = self.get_word(self.sent1, node1)
      mc.lemmas[0] = self.get_lemma(self.sent1, node1)
      mc.pos_tags[0] = self.get_pos_tag(self.sent1, node1)
    elif instr == 'skip2':
      mc.words[1] = self.get_word(self.sent2, node2)
      mc.lemmas[1] = self.get_lemma(self.sent2, node2)
      mc.pos_tags[1] = self.get_pos_tag(self.sent2, node2)
    else:
      assert False, instr
    
    match_tree.append(mc)
    # yes, the indices are 1-based here
    index = len(match_tree)
    for o1, o2 in succ:
      child_root, _ = self.get_match_tree(match_tree, o1, o2)
      if child_root is not None:
        assert child_root != index
        mc.children.append(child_root)
    if not mc.children:
      mc.children.append(0)
    return index, match_tree

  def print_match_path(self, node1=None, node2=None, indent=0):
    if node1 == None:
      node1 = self.root1
    if node2 == None:
      node2 = self.root2
    instr, succ = self.path_matrix[node1][node2]
    if node1 >= 1:
      word1 = self.get_word(self.sent1, node1)
    else:
      word1 = '.'
    if node2 >= 1:
      word2 = self.get_word(self.sent2, node2)
    else:
      word2 = '.'
    if instr.endswith('match'):
      print " " * indent + "%d,%d: %s: [%s <-> %s] (%d)" % (node1, node2, instr, word1, word2, self.score_matrix[node1, node2])
    elif instr == 'skip1':
      print " " * indent + "%d,%d: %s: %s (%d)" % (node1, node2, instr, word1, self.score_matrix[node1, node2])
    elif instr == 'skip2':
      print " " * indent + "%d,%d: %s: %s (%d)" % (node1, node2, instr, word2, self.score_matrix[node1, node2])
    elif instr == 'end':
      pass
    else:
      assert False, instr
    for o1, o2 in succ:
      assert (o1, o2) != (node1, node2), str(succ)
      self.print_match_path(o1, o2, indent+4)
