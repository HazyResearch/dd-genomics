#! /usr/bin/env python

import numpy as np
from sw_util import AlignmentMixin, MatchCell

class MultiDepAlignment(AlignmentMixin):

  word_match_score = 5
  dict_match_score = 5
  lemma_match_score = 5
  pos_tag_match_score = 1
  skip_score = -3
  mismatch_score = -5
  cand_match_score = 15
  
  def __init__(self, mt_root, match_tree, sent3, cands3, dicts):
    self.match_tree = match_tree
    self.sent3 = sent3
    self.dep3 = self.sent3['dependencies']
    self.cands3 = cands3
    self.dicts = dicts
    
    self.empty_cell = MatchCell(match_tree[0].size)
    
    self.score_matrix = np.empty((len(match_tree)+1, len(self.sent3['words'])+1))
    self.score_matrix[:] = np.inf
    self.path_matrix = [[('_', 0) for _ in xrange(len(sent3['words']) + 1)] for _ in xrange(len(match_tree) + 1)]
    for d in dicts:
      assert isinstance(d, set)

    self.mt_root = mt_root
    self.root3 = self.find_root(self.dep3)
    self.children3 = self.find_children(self.sent3)

    # 0 is implicitly root of a match tree
    self._h(self.mt_root, self.root3)
    
  def get_match_cell(self, mt_node):
    if mt_node == 0:
      return self.empty_cell
    else:
      return self.match_tree[mt_node - 1]
    
  def _match_score(self, mt_node, node3):
    mc = self.get_match_cell(mt_node)
    word3 = self.get_word(self.sent3, node3)
    lemma3 = self.get_lemma(self.sent3, node3)
    pos_tag3 = self.get_pos_tag(self.sent3, node3)

    sum_score = 0
    match_type = ''
    for i in xrange(len(mc.words)):
      if mc.words[i] is None:
        sum_score += self.skip_score
        match_type += '[skip%d];' % i
        continue
      broken = False
      for j in xrange(len(self.cands3)):
        if mc.cands[i] == j and node3 == self.cands3[j]:
          sum_score += self.cand_match_score
          match_type += '[cand%d_%d];' % (i, j)
          broken = True 
          break
      if broken:
        continue
      if mc.pos_tags[i] == pos_tag3 and mc.words[i] == word3:
        match_type += '[word%d];' % i 
        sum_score += self.word_match_score
        continue
      if mc.pos_tags[i] == pos_tag3 and mc.lemmas[i] == lemma3:
        match_type += '[lemma%d];' % i 
        sum_score += self.lemma_match_score
        continue
      if self.in_dicts(mc.words[i], word3, self.dicts):
        match_type += '[word_dict%d];' % i 
        sum_score += self.dict_match_score
        continue
      if self.in_dicts(mc.lemmas[i], lemma3, self.dicts):
        match_type += '[lemma_dict%d];' % i 
        sum_score += self.dict_match_score
        continue
      if mc.pos_tags[i] == pos_tag3:
        match_type += '[pos_tags%d];' % i 
        sum_score += self.pos_tag_match_score
        continue
      match_type += '[mis%d];' % i 
      sum_score += self.mismatch_score
    return sum_score, match_type + '_match'
  
  def _match(self, mt_node, node3):
    if mt_node == 0 and node3 == 0:
      return 0, 'end', []
    if mt_node == 0 and node3 != 0:
      return -1000, 'assert_false', []
    if mt_node != 0 and node3 == 0:
      return -1000, 'assert_false', []
    score_list = []
  
    mc = self.get_match_cell(mt_node)
    c1 = set(mc.children)
    assert mt_node not in c1, (mt_node, c1)
    c2 = set(self.children3[node3])
    assert node3 not in c2, (mt_node, c2)
  
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
    
    direct_match_score, match_type = self._match_score(mt_node, node3)
    assert len(outgoing) >= len(mc.children)
    assert len(outgoing) >= len(self.children3[node3])
    for o1, o2 in outgoing:
      assert mt_node != o1
      assert node3 != o2

    return direct_match_score + sum_score, match_type, outgoing
  
  def _skip1(self, mt_node, node3):
    if mt_node == 0 and node3 == 0:
      return -1000, 'assert_false', []
    if mt_node == 0 and node3 != 0:
      return -1000, 'assert_false', []
    score_list = []
    mc = self.get_match_cell(mt_node)
  
    for i in mc.children:
      self._h(i, node3)
      score_list.append((self.score_matrix[i, node3], i))
    score_list = sorted(score_list)[::-1]

    assert score_list[0][1] != mt_node, str((score_list[0][1], mt_node))
    return self.skip_score + score_list[0][0], 'skip1', [(score_list[0][1], node3)]
  
  def _skip2(self, mt_node, node3):
    if mt_node == 0 and node3 == 0:
      return -1000, 'assert_false', []
    if mt_node != 0 and node3 == 0:
      return -1000, 'assert_false', []
    score_list = []
  
    for j in self.children3[node3]:
      assert j != node3
      self._h(mt_node, j)
      score_list.append((self.score_matrix[mt_node, j], j))
    score_list = sorted(score_list)[::-1]
    
    mc = self.get_match_cell(mt_node)
    sum_score = 0
    skip_type = ''
    for i, word in enumerate(mc.words):
      if word is not None:
        skip_type += '[skip%d]' % i
        sum_score += self.skip_score
      else:
        skip_type += '[zero%d]' % i
    
    assert score_list[0][1] != node3, str((node3, score_list[0][1]))
    return sum_score + score_list[0][0], skip_type + '_skip2', [(mt_node, score_list[0][1])]
  
  def _h(self, mt_node, node3):
    if self.score_matrix[mt_node, node3] != np.inf:
      return self.score_matrix[mt_node, node3]
  
    m, match_type, cont_match = self._match(mt_node, node3)
    assert mt_node not in [c[0] for c in cont_match]
    assert node3 not in [c[1] for c in cont_match]
    l1, skip_type1, cont_skip1 = self._skip1(mt_node, node3)
    assert (mt_node, node3) not in cont_skip1
    l2, skip_type2, cont_skip2 = self._skip2(mt_node, node3)
    assert (mt_node, node3) not in cont_skip2
    
    score = max([m, l1, l2])
    
    self.score_matrix[mt_node, node3] = score
    if score == m:
      self.path_matrix[mt_node][node3] = match_type, cont_match
    elif score == l1:
      self.path_matrix[mt_node][node3] = skip_type1, cont_skip1
    elif score == l2:
      self.path_matrix[mt_node][node3] = skip_type2, cont_skip2
    else:
      assert False
      
  def print_match_path(self, mt_node=None, node3=None, indent=0):
    if mt_node == None:
      mt_node = self.mt_root
    if node3 == None:
      node3 = self.root3
    mc = self.get_match_cell(mt_node)
    
    instr, succ = self.path_matrix[mt_node][node3]
    if mt_node >= 1:
      mt_words = mc.words
    else:
      mt_words = ['.'] * mc.size
    if node3 >= 1:
      word3 = self.get_word(self.sent3, node3)
    else:
      word3 = '.'
      
    if instr.endswith('match'):
      print " " * indent + "%d,%d: %s: %s (%d)" % (mt_node, node3, instr, str(mt_words + [word3]), self.score_matrix[mt_node, node3])
    elif instr == 'skip1':
      print " " * indent + "%d,%d: %s: %s (%d)" % (mt_node, node3, instr, str(mt_words), self.score_matrix[mt_node, node3])
    elif instr.endswith('skip2'):
      print " " * indent + "%d,%d: %s: %s (%d)" % (mt_node, node3, instr, str([word3]), self.score_matrix[mt_node, node3])
    elif instr == 'end':
      pass
    else:
      assert False, instr
    for o1, o2 in succ:
      assert (o1, o2) != (mt_node, node3), str(succ)
      self.print_match_path(o1, o2, indent+4)
