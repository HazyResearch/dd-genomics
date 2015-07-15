from collections import defaultdict

# TODO: handle negations (neg, advmod + neg word) specially!

# See: http://nlp.stanford.edu/software/dependencies_manual.pdf

MAX_PATH_LEN = 100

class DepPathDAG:
  def __init__(self, dep_parents, dep_paths, words, max_path_len=None, no_count_tags=('conj',), no_count_words=('_','*',)):
    self.max_path_len = max_path_len
    self.no_count_tags = tuple(no_count_tags)
    self.no_count_words = no_count_words
    self.words = words
    self.edges = defaultdict(list)
    self.edge_labels = {}
    for i,dp in enumerate(dep_parents):
      if dp > 0:
        self.edges[i].append(dp-1)
        self.edges[dp-1].append(i)
        self.edge_labels[(i,dp-1)] = dep_paths[i]
        self.edge_labels[(dp-1,i)] = dep_paths[i]

  def _path_len(self, path):
    """Get the length of a list of nodes, skipping counting of certain dep path types"""
    l = 1
    for i in range(len(path)-1):
      if self.edge_labels[(path[i], path[i+1])].startswith(self.no_count_tags):
        continue
      if self.words[i] in self.no_count_words:
        continue
      l += 1
    return l

  def min_path(self, i, j, path=[]):
    if self.max_path_len and len(path) > self.max_path_len:
      return None
    min_path_len = MAX_PATH_LEN
    min_path = None
    for node in self.edges[i]:
      if node in path:
        continue
      elif node == j:
        return [j]
      else:
        p = self.min_path(node, j, path+[i])
        if p and self._path_len(p) < min_path_len:
          min_path = [node] + p
          min_path_len = self._path_len(min_path)
    return min_path

  def min_path_sets(self, idx, jdx):
    """Return the minimum path between the closest members of two sets of indexes"""
    min_path_len = None
    min_path = None
    if len(idx) == 0 or len(jdx) == 0:
      return min_path
    for i in idx:
      for j in jdx:
        p = self.min_path(i,j)
        l = self._path_len(p) if p else None
        if l and (min_path_len is None or l < min_path_len):
          min_path_len = l
          min_path = p
    return min_path

  def path_len(self, i, j):
    """Get the 'path length' i.e. the length of the min path between i and j"""
    min_path = self.min_path(i, j)
    return self._path_len(min_path) if min_path else None
    
  def path_len_sets(self, idx, jdx):
    """Return the path length (length of minimum path) between the closest
    members of two sets of indexes"""
    min_path = self.min_path_sets(idx,jdx)
    return self._path_len(min_path) if min_path else None

  def neighbors(self, idx):
    """Return the indices or neighboring words (0-indexed return value)"""
    rv = []
    for i in xrange(0, len(self.edges)):
      if idx in self.edges[i]:
        rv.append(i)
    return rv
