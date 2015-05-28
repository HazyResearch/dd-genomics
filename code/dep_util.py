import extractor_util
from itertools import groupby
from operator import itemgetter
from collections import defaultdict

class DepPathDAG:
    def __init__(self, words, dep_paths, dep_parents):
        self.dep_labels = dep_paths
        self.roots = []
        self.words = words
        self.edges = defaultdict(list)

        for i, dep_parent in enumerate(dep_parents):
            dep_parent = int(dep_parent)
            if dep_parent == -1:
                self.roots.append(i)
            else:
                self.edges[dep_parent].append(i)

# These functions are to manipulate dependency paths to ease the construction of features.

# Given a candidate mention (n-gram), find the closest contiguous sequence of a specified
# POS tag in the dependency path. If two are equally close, it returns the first.
# Input:
# mention (namedtuple from extractor_util)
# sentence (namedtuple from extractor_util)
# dep_path_dag (DepPathDAG)
# pos (pos for which you are searching)
# Output:
# words (words comprising phrase), indices (indices comprising phrase)
# or None
def find_closest_phrase_by_pos(mention, sentence, dep_path_dag, pos):
    if pos not in dep_path_dag.dep_labels: return None

    mention_middle = (mention.wordidxs[0] + mention.wordidxs[-1]) / 2
    pos_matches = [ind for ind in xrange(len(dep_path_dag.dep_path)) if dep_path_dag.dep_path[ind] == pos]

    # Transform something like [1,2,3,5,6,7,11] to [(1,3), (5,7), (11)] so we can identify phrases.
    ranges = []
    for key, group in groupby(enumerate(pos_matches), lambda (index, item): index - item):
        group = map(itemgetter(1), group)
        if len(group) > 1:
            ranges.append((group[0], group[-1]))
        else:
            ranges.append((group[0], group[0]))

    ranges.sort(key=lambda interval: min(abs(interval[0]-mention_middle), abs(interval[1]-mention_middle)))
    return [sentence.words[ind] for ind in ranges[0]], [i for i in ranges[0]]

def find_shortest_path(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if not graph.has_key(start):
            return None
        shortest = None
        for node in graph[start]:
            if node not in path:
                newpath = find_shortest_path(graph, node, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest

def find_shortest_path_length(graph, start, end):
    best_path = find_shortest_path(graph, start, end)
    if best_path is not None:
        return len(best_path)
    return len(find_shortest_path(graph, end, start))

# Given a list of keywords, if the keyword appears in a given sentence make it a feature
# but with its distance in the dependency tree to the first word of the candidate mention.
# Input:
# keywords (list of keywords)
# sentence (namedtuple from extractor_util)
# dep_path_dag (DepPathDAG)
# mention (namedtuple from extractor_util)
# Output:
# generator of features
def extract_features_using_keywords(keywords, sentence, dep_path_dag, mention):
    mention_start = mention.wordidxs[0]
    for i, word in enumerate(sentence.words):
        if word in keywords:
            path_length = find_shortest_path_length(dep_path_dag.edges, i, mention_start)
            yield 'FEATURE_CLOSE_%s_DIST_%s' % (word, path_length)
