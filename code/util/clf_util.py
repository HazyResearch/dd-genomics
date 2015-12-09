import dependencies
import sys

def index_of_sublist(subl, l):
    for i in range(len(l) - len(subl) + 1):
        if subl == l[i:i + len(subl)]:
            return i

def intersects(a1, a2):
    for i in a1:
        if i in a2:
            return True
    return False

def acyclic(a):
    return len(a) == len(set(a))
  
def create_sentence_index(row):
    sentence = {
        'words' : row.words,
        'lemmas' : row.lemmas,
        'poses' : row.poses,
        'dep_paths' : row.dep_paths,
        'dep_parents' : [ p-1 for p in row.dep_parents]
    }
    parents, children = dependencies.build_indexes(sentence)
    index = {
        'sentence': sentence,
        'parents': parents,
        'children': children }
    return index

def supervise(m, cands, sentence_index, doc, pos_phrases, neg_phrases, pos_dep_patterns, neg_dep_patterns, dicts):
    labeling = None
    sentence = sentence_index['sentence']
    parents = sentence_index['parents']
    children = sentence_index['children']

    for p in pos_phrases:
        start = index_of_sublist(p, sentence['words'])
        if start is not None:
            match_indices = range(start, start + len(p))
            if intersects(match_indices, m.wordidxs):
                labeling = True

    for p in neg_dep_patterns:
        matches = []
        dependencies.match(sentence, p, cands, parents, children, matches, dicts)
        for ma in matches:
            if intersects(ma, m.wordidxs):
                labeling = False

    for p in pos_dep_patterns:
        matches = []
        dependencies.match(sentence, p, cands, parents, children, matches, dicts)
        for ma in matches:
            if intersects(ma, m.wordidxs):
                if labeling is None:
                    labeling = True

    return m._replace(is_correct=labeling)

def featurize(m, cands, sentence_index, feature_patterns, bad_features, dicts):
    sentence = sentence_index['sentence']
    parents = sentence_index['parents']
    children = sentence_index['children']

    feature_set = set()

    # find dependency path that covers wordidxs, lemmatize

    # feature = ''
    # for i in m.wordidxs:
    #    m.features.append(sentence['lemmas'][i])
    #    for p in parents[i]:
    #        path, parent = p
    #        if parent in m.wordidxs:
    #            feature = feature + sentence['lemmas'][i] + '<-' + path + '-' + sentence['lemmas'][parent] + '|||'

    # if feature != '':
    #    m.features.append(feature)

    feature_prefix = ''
    for i in m.wordidxs:
        for c in children[i]:
            path, child = c
            if path == 'neg':
                feature_prefix = 'NEGATED'

    # for i in m.wordidxs:
    #     for c in children[i]:
    #         path, child = c
    #         if path == 'neg':
    #             feature_set.add('NEGATED')
    # for i in m.wordidxs:
    #     if sentence['poses'][i] == 'NNS':
    #         feature_set.add('PLURAL')
    # for i in m.wordidxs:
    #     for p in parents[i]:
    #         path, parent = p
    #         if sentence['poses'][parent] == 'NNS':
    #             feature_set.add('MOD_PLURAL')

    def get_actual_dep_from_match(pattern, j, ma):
        # determine the edge
        edge_pattern = pattern[2 * j + 1]
        if edge_pattern[:2] == '<-':
            # print(str(ma[j]), file=sys.stderr)
            # print(str(parents[ma[j]]), file=sys.stderr)
            dep = '<-' + parents[ma[j]][0][0] + '-'
        elif edge_pattern[len(edge_pattern) - 2:] == '->':
            dep = '-' + parents[ma[j + 1]][0][0] + '->'
        elif edge_pattern == '_':
            dep = '_'
        else:
            print >> sys.stderr, 'ERROR: Unknown edge pattern'
        return dep

    # pattern = '__ <-prep_like- __ -nsubj-> __'.split(' ')
    # for pattern in feature_patterns:
    #    for i in m.wordidxs:
    #        matches = []
    #        dependencies.match_i(sentence, i, pattern, parents, children, matches, [], dicts)
    #        for ma in matches:
    #            #feature = '__' + pattern[1]
    #            feature = sentence['lemmas'][ma[0]] + get_actual_dep_from_match(pattern, 0, ma)
    #            j = 1
    #            while j < len(ma):
    #                feature = feature + sentence['lemmas'][ma[j]]
    #                if 2*j + 1 < len(pattern):
    #                   dep = get_actual_dep_from_match(pattern, 0, ma)
    #                   feature = feature + dep
    #                j = j+1
    #            m.features.append(feature)

    # pattern = '__ <-prep_like- __ -nsubj-> __'.split(' ')
    for pattern in feature_patterns:
        matches = []
        dependencies.match(sentence, pattern, cands, parents, children, matches, dicts)
        for ma in matches:
            if intersects(m.wordidxs, ma) and acyclic(ma):
                # feature = '__' + pattern[1]
                feature = sentence['lemmas'][ma[0]] + ' ' + get_actual_dep_from_match(pattern, 0, ma)
                j = 1
                while j < len(ma):
                    feature = feature + ' ' + sentence['lemmas'][ma[j]]
                    if 2 * j + 1 < len(pattern):
                        dep = get_actual_dep_from_match(pattern, j, ma)
                        feature = feature + ' ' + dep
                    j = j + 1
                feature_set.add(feature)

    for f in feature_set:
        if f in bad_features:
          continue
        m.features.append(feature_prefix + '_' + f)
    return m
