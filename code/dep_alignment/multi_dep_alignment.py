#! /usr/bin/env python

import numpy as np
from alignment_util import AlignmentMixin, MatchCell
import sys

class MultiDepAlignment(AlignmentMixin):

  word_match_score = 5
  dict_match_score = 5
  lemma_match_score = 5
  pos_tag_match_score = 1
  skip_score = -3
  mismatch_score = -5
  cand_match_score = 15
  
  def __init__(self, mt_root1, match_tree1, mt_root2, match_tree2, num_cands, dicts):
    self.match_tree1 = match_tree1
    self.match_tree2 = match_tree2
    self.dicts = dicts
    self.num_cands = num_cands
    
    self.empty_cell1 = MatchCell(match_tree1[0].size)
    self.empty_cell2 = MatchCell(match_tree2[0].size)
    
    self.score_matrix = np.empty((len(match_tree1)+1, len(match_tree2)+1))
    self.score_matrix[:] = np.inf
    self.path_matrix = [[('_', 0) for _ in xrange(len(match_tree2)+1)] for _ in xrange(len(match_tree1)+1)]
    for d in dicts:
      assert isinstance(d, set)

    self.mt_root1 = mt_root1
    self.mt_root2 = mt_root2

    # 0 is implicitly root of a match tree
    self._h(self.mt_root1, self.mt_root2)
    
  def get_match_cell1(self, mt_node1):
    if mt_node1 == 0:
      return self.empty_cell1
    else:
      return self.match_tree1[mt_node1 - 1]
    
  def get_match_cell2(self, mt_node2):
    if mt_node2 == 0:
      return self.empty_cell2
    else:
      return self.match_tree2[mt_node2 - 1]
    
  def _match_score(self, mt_node1, mt_node2):
    mc1 = self.get_match_cell1(mt_node1)
    mc2 = self.get_match_cell2(mt_node2)

    sum_score = 0
    match_type = ''
    for i in xrange(len(mc1.words)):
      for j in xrange(len(mc2.words)):
        if mc1.words[i] is None and mc2.words[j] is None:
          match_type += '[gaps%d,%d];' % (i, j)
          continue
        if mc1.words[i] is None and mc2.words[j] is not None:
          sum_score += self.skip_score
          match_type += '[gap1%d,%d];' % (i, j)
          continue
        if mc1.words[i] is not None and mc2.words[j] is None:
          sum_score += self.skip_score
          match_type += '[gap2%d,%d];' % (i, j)
          continue
        broken = False
        for k in xrange(self.num_cands):
          if mc1.cands[i] == k and mc2.cands[j] == k:
            sum_score += self.cand_match_score
            match_type += '[cand%d,%d_%d];' % (i, j, k)
            broken = True 
            break
        if broken:
          continue
        if mc1.pos_tags[i] == mc1.pos_tags[j] and mc1.words[i] == mc2.words[j]:
          match_type += '[word%d,%d];' % (i, j) 
          sum_score += self.word_match_score
          continue
        if mc1.pos_tags[i] == mc2.pos_tags[j] and mc1.lemmas[i] == mc2.lemmas[j]:
          match_type += '[lemma%d,%d];' % (i, j) 
          sum_score += self.lemma_match_score
          continue
        if self.in_dicts(mc1.words[i], mc2.words[j], self.dicts):
          match_type += '[word_dict%d,%d];' % (i, j) 
          sum_score += self.dict_match_score
          continue
        if self.in_dicts(mc1.lemmas[i], mc2.lemmas[j], self.dicts):
          match_type += '[lemma_dict%d,%d];' % (i, j) 
          sum_score += self.dict_match_score
          continue
        if mc1.pos_tags[i] == mc2.pos_tags[j]:
          match_type += '[pos_tags%d,%d];' % (i, j) 
          sum_score += self.pos_tag_match_score
          continue
        match_type += '[mis%d,%d];' % (i, j) 
        sum_score += self.mismatch_score
    return sum_score, match_type + '_match'
  
  def _match(self, mt_node1, mt_node2):
    if mt_node1 == 0 and mt_node2 == 0:
      return 0, 'end', []
    if mt_node1 == 0 and mt_node2 != 0:
      return -1000, 'assert_false', []
    if mt_node1 != 0 and mt_node2 == 0:
      return -1000, 'assert_false', []
    score_list = []
  
    mc1 = self.get_match_cell1(mt_node1)
    c1 = set(mc1.children)
    assert mt_node1 not in c1, (mt_node1, c1)
    mc2 = self.get_match_cell2(mt_node2)
    c2 = set(mc2.children)
    assert mt_node2 not in c2, (mt_node2, c2)
  
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
    
    direct_match_score, match_type = self._match_score(mt_node1, mt_node2)
    assert len(outgoing) >= len(mc1.children)
    assert len(outgoing) >= len(mc2.children)
    for o1, o2 in outgoing:
      assert mt_node1 != o1, (mt_node1, o1, match_type, mc1.children)
      assert mt_node2 != o2, (mt_node2, o2, match_type, mc2.children)

    return direct_match_score + sum_score, match_type, outgoing
  
  def _skip1(self, mt_node1, mt_node2):
    if mt_node1 == 0 and mt_node2 == 0:
      return -1000, 'assert_false', []
    if mt_node1 == 0 and mt_node2 != 0:
      return -1000, 'assert_false', []
    score_list = []
    mc1 = self.get_match_cell1(mt_node1)
  
    for i in mc1.children:
      assert i != mt_node1
      self._h(i, mt_node2)
      score_list.append((self.score_matrix[i, mt_node2], i))
    score_list = sorted(score_list)[::-1]
    
    mc2 = self.get_match_cell2(mt_node2)
    sum_score = 0
    skip_type = ''
    for j, word in enumerate(mc2.words):
      if word is not None:
        skip_type += '[skip%d]' % j
        sum_score += self.skip_score
      else:
        skip_type += '[zero%d]' % j

    assert score_list[0][1] != mt_node1, str((score_list[0][1], mt_node1))
    return sum_score + score_list[0][0], skip_type + '_skip1', [(score_list[0][1], mt_node2)]
  
  def _skip2(self, mt_node1, mt_node2):
    if mt_node1 == 0 and mt_node2 == 0:
      return -1000, 'assert_false', []
    if mt_node1 != 0 and mt_node2 == 0:
      return -1000, 'assert_false', []
    score_list = []
    mc2 = self.get_match_cell2(mt_node2)
  
    for j in mc2.children:
      assert j != mt_node2
      self._h(mt_node1, j)
      score_list.append((self.score_matrix[mt_node1, j], j))
    score_list = sorted(score_list)[::-1]
    
    mc1 = self.get_match_cell1(mt_node1)
    sum_score = 0
    skip_type = ''
    for i, word in enumerate(mc1.words):
      if word is not None:
        skip_type += '[skip%d]' % i
        sum_score += self.skip_score
      else:
        skip_type += '[zero%d]' % i
    
    assert score_list[0][1] != mt_node2, str((mt_node2, score_list[0][1]))
    return sum_score + score_list[0][0], skip_type + '_skip2', [(mt_node1, score_list[0][1])]
  
  def _h(self, mt_node1, mt_node2):
    if self.score_matrix[mt_node1, mt_node2] != np.inf:
      return self.score_matrix[mt_node1, mt_node2]
  
    m, match_type, cont_match = self._match(mt_node1, mt_node2)
    assert mt_node1 not in [c[0] for c in cont_match]
    assert mt_node2 not in [c[1] for c in cont_match]
    l1, skip_type1, cont_skip1 = self._skip1(mt_node1, mt_node2)
    assert (mt_node1, mt_node2) not in cont_skip1, (mt_node1, mt_node2, cont_skip1)
    l2, skip_type2, cont_skip2 = self._skip2(mt_node1, mt_node2)
    assert (mt_node1, mt_node2) not in cont_skip2, (mt_node1, mt_node2, cont_skip2)
    
    score = max([m, l1, l2])
    
    self.score_matrix[mt_node1, mt_node2] = score
    if score == m:
      self.path_matrix[mt_node1][mt_node2] = match_type, cont_match
    elif score == l1:
      self.path_matrix[mt_node1][mt_node2] = skip_type1, cont_skip1
    elif score == l2:
      self.path_matrix[mt_node1][mt_node2] = skip_type2, cont_skip2
    else:
      assert False
      
  def print_match_path(self, stream=sys.stdout, mt_node1=None, mt_node2=None, indent=0):
    if mt_node1 == None:
      mt_node1 = self.mt_root1
    if mt_node2 == None:
      mt_node2 = self.mt_root2
    mc1 = self.get_match_cell1(mt_node1)
    mc2 = self.get_match_cell2(mt_node2)
    
    instr, succ = self.path_matrix[mt_node1][mt_node2]
    if mt_node1 >= 1:
      mt_words1 = mc1.words
    else:
      mt_words1 = ['.'] * mc1.size
    if mt_node2 >= 1:
      mt_words2 = mc2.words
    else:
      mt_words2 = '.' * mc2.size
      
    if instr.endswith('match'):
      print >>stream, " " * indent + "%d,%d: %s: %s (%d)" % (mt_node1, mt_node2, instr, str(mt_words1 + mt_words2), self.score_matrix[mt_node1, mt_node2])
    elif instr.endswith('skip1'):
      print >>stream, " " * indent + "%d,%d: %s: %s (%d)" % (mt_node1, mt_node2, instr, str(mt_words1), self.score_matrix[mt_node1, mt_node2])
    elif instr.endswith('skip2'):
      print >>stream, " " * indent + "%d,%d: %s: %s (%d)" % (mt_node1, mt_node2, instr, str(mt_words2), self.score_matrix[mt_node1, mt_node2])
    elif instr == 'end':
      pass
    else:
      assert False, instr
    for o1, o2 in succ:
      assert (o1, o2) != (mt_node1, mt_node2), str(succ)
      self.print_match_path(stream, o1, o2, indent+4)
  
  def overall_score(self):
    return self.score_matrix[self.mt_root1, self.mt_root2]