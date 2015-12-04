#! /usr/bin/env python3

######################################################################################
#  LATTICE - latticelib.py: Extractor framework utility
#
#  latticelib is an extraction framework to allow quickly building extractors by
#  specifying minimal target-specific code (candidate generation patterns and
#  supervision rules). It has a set of pre-built featurization code that covers
#  a range of different extractors. The goal is to make it more general,
#  powerful, fast to run and easy to use.
#
#  Currently latticelib supports only mention-level extractors. relation-level
#  and document-level will be supported later.
#
#  For sample usage, see:
#      udf/util/test/test_latticelib.py
#      udf/extract_underage.py
#
######################################################################################

import sys, os, re, json, collections

Document = collections.namedtuple('Document',
                                  ['doc_id', 'text', 'words', 'lemmas', 'poses',
                                   'ners', 'dep_paths', 'dep_parents'])
Mention = collections.namedtuple('Mention', ['doc_id', 'sent_id', 'wordidxs',
    'mention_id', 'type', 'entity', 'words', 'is_correct', 'features', 'misc'])

def set_misc(mention, key, value):
    mention.misc[key] = value

# Default dictionaries
default_dicts = {
    'intensifiers' : ['very', 'really', 'extremeley', 'amazingly',
        'exceptionally', 'incredibly', 'unusually', 'remarkably',
        'particularly', 'absolutely', 'completely', 'totally', 'utterly',
        # 'quite',
        'definitely', 'too', 'so', 'super'],
    'negation': ['not', 'never', 'nothing', 'no', 'none', 'barely',
        'hardly'],
    'count' : ['first', 'second', 'third', '1st', '2nd', '3rd'],
    }


default_feature_patterns = [
    'CAND_PATTERN',
    'NEGATED',
    'PLURAL',
    'MOD_PLURAL',
    '__ <-__- __',
    '__ <-__- __ -__-> __',
    '__ _ __',
    '__ _ __ _ __',
    '__ _ __ _ __ _ __',
    '__ _ __ _ __ _ __ _ __'
]

default_input_columns = ['doc_id', 'text', 'words', 'lemmas', 'poses', 'ners',
    'sent_token_offsets', 'dependencies']

# A latticelib config object
class Config(object):
    '''
    Sample:

    from util import latticelib

    config = latticelib.Config()

    config.set_pos_patterns([
        '[dic:intensifiers] <-advmod- young',
        'she _ is _ 18'
    ])

    config.set_neg_patterns([
        'not <-neg- young',
        'isnt _ very _ young'
    ])

    config.set_candidate_patterns([
        'underage', 'young', 'kid', 'child',
        '[dic:intensifiers] <-advmod- young'
        ])

    config.run()

    '''


    def __init__(self, module = None):

        self._frozen = False

        # For featurization
        self.dicts = default_dicts.copy()
        self.feature_patterns = default_feature_patterns.copy()
        self.MAX_DIST = 5 # for computing arbitrary dep paths between two words
        self.NGRAM_WILDCARD = True
        self.PRINT_SUPV_RULE = False

        # For supervision
        self.ordered_patterns = None
        self.use_ordered_supervision = False
        self.pos_patterns = []
        self.neg_patterns = []
        self.strong_pos_patterns = []
        self.strong_neg_patterns = []
        self.pos_phrases = []
        self.neg_phrases = []

        # Set the columns in input
        self.input_columns = default_input_columns

        # For candidate generation
        self.candidate_patterns = []

        # Overridable functions
        self.extract_candidates = default_extract_candidates
        self.supervise = default_supervise
        self.featurizers = [default_featurize]

        self.input_stream = sys.stdin

        # Allow a module to specify defaults
        if module is not None:
            if 'default_dicts' in dir(module):
                self.dicts.update(module.default_dicts)
            if 'default_feature_patterns' in dir(module):
                self.feature_patterns = module.default_feature_patterns.copy()
            if 'default_extract_candidates' in dir(module):
                self.extract_candidates = module.default_extract_candidates
            if 'default_supervise' in dir(module):
                self.supervise = module.default_supervise
            if 'default_featurize' in dir(module):
                self.featurizers = [module.default_featurize]

    def add_dict(self, key, values):
        '''
        key: the key for dictionary
        values: a list of words in this dictionary

        Note: if there is a key that exists in the previous dicts, the whole
        dict will be replaced.
        '''
        self.dicts[key] = list(values)

    def add_value_to_dict(self, key, value):
        '''
        key: the key for dictionary
        value: one specific value to add into a dictionary. If the dictionary does not exist, create it.

        Note: if there is a key that exists in the previous dicts, the whole dict will be replaced.
        '''
        if key not in self.dicts:
            self.dicts[key] = []

        self.dicts[key].append(value)

    def add_dicts(self, dicts):
        '''
        add the specified dicts to the current dicts.

        Note: if there is a key that exists in the previous dicts, the whole
        dict will be replaced.
        '''
        self.dicts.update(dicts)

    def set_dicts(self, dicts):
        '''
        add the specified dicts to the current dicts.

        Note: if there is a key that exists in the previous dicts, the whole
        dict will be replaced.
        '''
        self.dicts = dicts

    def set_pos_patterns(self, patterns):
        '''
        Set the pos_patterns to the specified patterns as an unordered list.
        '''
        self.pos_patterns = list(patterns)

    def set_neg_patterns(self, patterns):
        '''
        Set the neg_patterns to the specified patterns as an unordered list.
        '''
        self.neg_patterns = list(patterns)

    def set_strong_pos_patterns(self, patterns):
        '''
        Set the strong_pos_patterns to the specified patterns as an unordered list.
        '''
        self.strong_pos_patterns = list(patterns)

    def set_strong_neg_patterns(self, patterns):
        '''
        Set the strong_neg_patterns to the specified patterns as an unordered list.
        '''
        self.strong_neg_patterns = list(patterns)

    def set_pos_supervision_phrases(self, phrases):
        '''
        Specify a list of positive phrases to directly supervise a mention as
        top priority
        '''
        self.pos_phrases = list(phrases)

    def set_neg_supervision_phrases(self, phrases):
        '''
        Specify a list of negative phrases to directly supervise a mention as
        top priority
        '''
        self.neg_phrases = list(phrases)


    def set_ordered_patterns(self, ordered_patterns):
        '''
        Set a list of positive and negative patterns that is an ordered
        list of following tuples:

            (True/False, pattern)

        where the first item in the tuple denotes whether to supervise
        this example as true or false.

        Note: if this method is called, the library will perform
        supervision by ordered match of these rules.
        If other methods are called, it will perform supervision by counting positive / negative matches.
        '''
        self.ordered_patterns = ordered_patterns
        raise NotImplementedError


    def set_candidate_patterns(self, patterns):
        '''
        Set the candidate_patterns to the specified patterns as an unordered list.
        '''
        self.candidate_patterns = patterns

    def set_feature_patterns(self, patterns):
        '''
        Set the feature_patterns to the specified patterns as an unordered list.
        '''
        self.feature_patterns = patterns

    def add_feature_patterns(self, patterns):
        '''
        Set the feature_patterns to the specified patterns as an unordered list.
        '''
        self.feature_patterns += list(patterns)


    def set_candidate_generator(self, func):
        '''
        Use a specified function to replace the default candidate generation function.

        The specified "func" should take two inputs:
          - sentence_index: built from latticelib.build_indexes
          - doc: built from latticelib.build_doc_from_nlp_line

        "func" should return a list of namedtuple latticelib.Mention.

        '''
        self.extract_candidates = func

    def set_supervisor(self, func):
        '''
        Use a specified function to replace the default supervision function.

        The specified "func" should take two inputs:
          - sentence_index: built from latticelib.build_indexes
          - doc: built from latticelib.build_doc_from_nlp_line

        "func" should return a list of namedtuple latticelib.Mention.

        '''
        self.supervise = func

    def set_featurizers(self, funcs):
        '''
        Use a list of specified functions to replace the default featurize function.

        The specified "func" should take two inputs:
          - sentence_index: built from latticelib.build_indexes
          - doc: built from latticelib.build_doc_from_nlp_line

        "func" should return a list of namedtuple latticelib.Mention.

        '''
        assert type(funcs) == list
        self.featurizers = funcs.copy()

    def add_featurizer(self, func):
        '''
        Use a specified function to replace the default featurize function.

        The specified "func" should take two inputs:
          - sentence_index: built from latticelib.build_indexes
          - doc: built from latticelib.build_doc_from_nlp_line

        "func" should return a list of namedtuple latticelib.Mention.

        '''
        self.featurizers.append(func)

    def set_input_stream(self, input_stream):
        '''
        Set the input stream. By default it is sys.stdin
        '''
        self.input_stream = input_stream

    def set_input_columns(self, input_columns):
        '''
        Set the columns from the input stream. Default is:
          ['doc_id', 'text', 'words', 'lemmas', 'poses',
            'ners', 'sent_token_offsets', 'dependencies']
        '''
        self.input_columns = input_columns

    def _freeze(self):

        '''
        A method called at the beginning of candidate generation.
        After this, one cannot perform changes to this config.
        '''

        self.pos_patterns = [ p.split(' ') for p in self.pos_patterns ]
        self.neg_patterns = [ p.split(' ') for p in self.neg_patterns ]
        self.strong_pos_patterns = [ p.split(' ') for p in self.strong_pos_patterns ]
        self.strong_neg_patterns = [ p.split(' ') for p in self.strong_neg_patterns ]
        self.candidate_patterns = [ p.split(' ') for p in self.candidate_patterns ]

        if self.ordered_patterns is not None:
            self.use_ordered_supervision = True

        for i in self.dicts:
            self.dicts[i] = frozenset(self.dicts[i])

        # Allow single-word options
        for i in range(0, len(self.feature_patterns)):
            if ' ' in self.feature_patterns[i]:
                self.feature_patterns[i] = self.feature_patterns[i].split(' ')

        self._frozen = True


    def run(self):
        '''
        Run the pipeline.
        '''
        self._freeze()
        for line in self.input_stream:
            try:
                doc = build_doc_from_nlp_line(line, self.input_columns)
            except Exception as e:
                # print(e.message)
                raise e

            sentence_index = create_sentence_index(doc)
            mentions = self.extract_candidates(sentence_index, doc, self)
            for featurizer in self.featurizers:
                mentions = featurizer(mentions, sentence_index, doc, self)
            mentions = self.supervise(mentions, sentence_index, doc, self)

            # convert sentence wordidxs to document-based wordidxs for mindtagger
            sent_token_offsets = []
            cur_offset = 0
            for sent_num in range(0, len(sentence_index)):
                sent_token_offsets.append(cur_offset)
                sentence = sentence_index[sent_num]['sentence']
                cur_offset = cur_offset + len(sentence['words'])
            for m in mentions:
                for i in range(0, len(m.wordidxs)):
                    m.wordidxs[i] = m.wordidxs[i] + sent_token_offsets[m.sent_id]

            for mention in mentions:
                print(tsv_dump_mention(mention))

def _get_column(parts, columns, key, required=False, is_json=True, escape=False):
    if len(parts) != len(columns):
        raise ValueError('Input has %d columns but configured %d columns.' % (len(parts), len(columns)))
    if key in columns:
        result = parts[columns.index(key)]
        if escape:
            result = result.replace('\\\\', '\\')
        if is_json:
            result = json.loads(result)
        return result

    else:
        if required:
            raise ValueError('Required field %s does not exist in input!' % key)
        else:
            return []

def build_doc_from_nlp_line(line, columns = default_input_columns):
    '''
    Converting a row from nlp table to the legacy format document.

    Columns: an array specifying the header of the input columns.

    Supported columns are:
    - doc_id
    - text
    - words
    - lemmas
    - poses
    - ners
    - sent_token_offsets
    - dependencies
    '''

    t = line.rstrip('\n').split('\t')
    # convert deps into dep_paths and dep_parents
    doc_id = _get_column(t, columns, 'doc_id', is_json=False)
    doc_text = _get_column(t, columns, 'text', is_json=False, escape=True)
    doc_tokens = _get_column(t, columns, 'words')
    doc_lemmas = _get_column(t, columns, 'lemmas')
    doc_poses = _get_column(t, columns, 'poses')
    doc_ners = _get_column(t, columns, 'ners')
    doc_sent_tok_offsets = _get_column(t, columns, 'sent_token_offsets')
    num_sents = len(doc_sent_tok_offsets)
    doc_deps = _get_column(t, columns, 'dependencies')
    doc_dep_paths = []
    doc_dep_parents = []
    doc_sent_tokens = []
    doc_sent_lemmas = []
    doc_sent_poses = []
    doc_sent_ners = []
    for i in range(0, num_sents):
        tok_begin = doc_sent_tok_offsets[i][0]
        tok_end = doc_sent_tok_offsets[i][1]
        num_toks = tok_end - tok_begin
        dep_paths = ['']*num_toks
        dep_parents = [0]*num_toks
        for d in doc_deps[i]:
            dep_paths[d['to']] = d['name']
            dep_parents[d['to']] = d['from'] + 1
        doc_dep_paths.append(dep_paths)
        doc_dep_parents.append(dep_parents)
        doc_sent_tokens.append(doc_tokens[tok_begin:tok_end])
        doc_sent_lemmas.append(doc_lemmas[tok_begin:tok_end])
        doc_sent_poses.append(doc_poses[tok_begin:tok_end])
        doc_sent_ners.append(doc_ners[tok_begin:tok_end])
    doc = Document(
        doc_id = doc_id,
        text = doc_text,
        words = doc_sent_tokens,
        lemmas = doc_sent_lemmas,
        poses = doc_sent_poses,
        ners=doc_sent_ners,
        dep_paths = doc_dep_paths,
        dep_parents = doc_dep_parents)

    return doc


def create_sentence_index(doc):
    '''
    Create sentence indexes from a doc
    '''
    index = []
    for sent_num in range(0, len(doc.words)):
        sentence = {
            'text': ' '.join(doc.words[sent_num]),
            'words' : doc.words[sent_num],
            'lemmas' : doc.lemmas[sent_num],
            'poses' : doc.poses[sent_num],
            'ners': doc.ners[sent_num],
            'dep_paths' : doc.dep_paths[sent_num],
            'dep_parents' : [ p-1 for p in doc.dep_parents[sent_num]]
        }
        parents, children = Dependencies.build_indexes(sentence)
        index.append({
            'sentence': sentence,
            'parents': parents,
            'children': children
        })
    return index



def default_extract_candidates(sentence_index, doc, config):
    '''
    Extract candidates from a specified sentence index, doc and config.
    '''
    mentions = []
    sent_token_offset = 0

    if not config._frozen:
        config._freeze()

    for sent_num in range(0, len(sentence_index)):
        sentence = sentence_index[sent_num]['sentence']
        parents = sentence_index[sent_num]['parents']
        children = sentence_index[sent_num]['children']

        # match dependency patterns

        # Do not generate duplicated mentions (with exact mid)
        matched_idxs = set()
        for p in config.candidate_patterns:
            matches = []
            Dependencies.match(sentence, p, parents, children, matches, config.dicts)
            for m in matches:
                # fix the gap if any
                if len(m) == 2 and max(m) -  min(m) > 1:
                    m = list(range(min(m), max(m) + 1))
                mention_id = doc.doc_id + '_' + str(sent_num) + '_' + '_'.join([str(i) for i in m])

                mention = Mention(
                    doc_id = doc.doc_id,
                    sent_id = sent_num,
                    wordidxs = m,
                    mention_id = mention_id,
                    type = '',
                    entity = '',
                    words = [ sentence['words'][i] for i in m ],
                    is_correct = None,
                    features = [],
                    misc = {}
                )
                if 'CAND_PATTERN' in config.feature_patterns:
                    mention.features.append('P:' + ''.join(p))

                if '_'.join([str(i) for i in m]) not in matched_idxs:
                    mentions.append(mention)
                    matched_idxs.add('_'.join([str(i) for i in m]))

        sent_token_offset = sent_token_offset + len(sentence['words'])

    return mentions


def default_supervise(mentions, sentence_index, doc, config):
    '''
    Perform supervision to all mentions using the specified sentence_index, doc, and config.
    '''
    if not config._frozen:
        config._freeze()

    # does it match one of our dicts ?
    num_pos = 0
    num_neg = 0
    n_mentions = []

    # mentions by sent_id
    sent_mentions = {}
    for m in mentions:
        l = sent_mentions.get(m.sent_id, [])
        l.append(m)
        sent_mentions[m.sent_id] = l


    # Return matches (wordidxs) or empty array
    def match_pattern(pattern, mentions):
        pattern = ' '.join(pattern)
        # TODO: separate pattern match and feature match
        tot_matches = set()
        if '_' in pattern or not any('[subj' in p or '[cand' in p or '[obj' in p for p in pattern):
            matches = []
            Dependencies.match(sentence, pattern, parents, children, matches, config.dicts)
            for m in matches:
                tot_matches.update(m)

        for m in mentions:
            if pattern in m.features:
                tot_matches.update(m.wordidxs)

        return list(tot_matches)

    for sent_num in range(0, len(sentence_index)):
        sentence = sentence_index[sent_num]['sentence']
        parents = sentence_index[sent_num]['parents']
        children = sentence_index[sent_num]['children']
        sm = sent_mentions.get(sent_num, [])
        if len(sm) == 0:
            continue

        # for p in config.pos_phrases:
        #     if p in sentence['text']:
        #         num_pos = num_pos + 1
        # skip the sentence if a certain pharase appears
        # print('neg_phrases = %s' % (' '.join(config.neg_phrases)), file=sys.stderr)
        # print('sent text=%s' % sentence['text'], file=sys.stderr)
        # for sentence in doc.text.split('\n'):
            # print('doc text = %s' % sentence, file=sys.stderr)
        if any(p in sentence['text'] for p in config.neg_phrases):
            continue
        # for p in config.neg_phrases:
        #     if p in sentence['text']:
        #         num_neg = num_neg + 1


        labeling = {}
        for m in sm:
            labeling[id(m)] = None

        for p in config.pos_patterns:
            matches = match_pattern(p, sm)
            num_pos = num_pos + len(matches)
            for m in sm:
                if _intersects(matches, m.wordidxs):
                    labeling[id(m)] = True
                    if config.PRINT_SUPV_RULE:
                        set_misc(m, 'rule', ' '.join(p))

        for p in config.strong_pos_patterns:
            matches = match_pattern(p, sm)
            num_pos = num_pos + len(matches)
            for m in sm:
                if _intersects(matches, m.wordidxs):
                    labeling[id(m)] = 'strong_pos'
                    if config.PRINT_SUPV_RULE:
                        set_misc(m, 'rule', ' '.join(p))

        for p in config.neg_patterns:
            matches = match_pattern(p, sm)
            num_neg = num_neg + len(matches)
            for m in sm:
                if _intersects(matches, m.wordidxs):
                    if labeling[id(m)] == True:
                        labeling[id(m)] = 'ambiguous'
                    elif labeling[id(m)] is None:
                        labeling[id(m)] = False
                    if config.PRINT_SUPV_RULE:
                        set_misc(m, 'rule', ' '.join(p))

        for p in config.strong_neg_patterns:
            matches = match_pattern(p, sm)
            num_pos = num_pos + len(matches)
            for m in sm:
                if _intersects(matches, m.wordidxs):
                    labeling[id(m)] = 'strong_neg'
                    if config.PRINT_SUPV_RULE:
                        set_misc(m, 'rule', ' '.join(p))

        for m in sm:
            l = labeling[id(m)]
            if l == 'ambiguous':
                l = None
            elif l == 'strong_pos':
                l = True
            elif l == 'strong_neg':
                l = False
            if l is None:
                if config.PRINT_SUPV_RULE:
                    set_misc(m, 'rule', None)

            n_mentions.append(m._replace(is_correct = l))

    return n_mentions


def default_featurize(mentions, sentence_index, doc, config):
    '''
    The default featurizer. Generates dependency features based on
    config.feature_patterns.

    Currently supports:
    * fixed-length dependency path
    * dependency sub-graph containing defined nodes and minimal paths between them
    '''
    if not config._frozen:
        config._freeze()

    # generate features based on feature patterns
    def _get_actual_dep_from_match(parents, pattern, j, ma):
        # e.g. pattern: ['__', '<-__-', '__']
        # determine the edge
        edge_pattern = pattern[2*j + 1]
        if edge_pattern[:2] == '<-':
            dep = '<-' + parents[ma[j]][0][0] + '-'
        elif edge_pattern[len(edge_pattern)-2:] == '->':
            dep = '-' + parents[ma[j+1]][0][0] + '->'
        elif edge_pattern == '_':
            dep = '_'
        else:
            print('ERROR: Unknown edge pattern', file=sys.stderr)
        return dep

    def _featurize_fixed_length_dependency(sentence, mention, patterns, parents, children, dicts):
        # TODO optimize?
        for pattern in patterns:
            matches = []
            Dependencies.match(sentence, pattern, parents, children, matches, config.dicts)
            for ma in matches:
                # print('MATCH:', ma)
                if _intersects(mention.wordidxs, ma) and _acyclic(ma):
                    # first version replaces every wildcard __ with a lemma
                    feature = sentence['lemmas'][ma[0]].lower() + ' ' + _get_actual_dep_from_match(parents, pattern, 0, ma)
                    j = 1
                    while j < len(ma):
                        feature = feature + ' ' + sentence['lemmas'][ma[j]].lower()
                        if 2*j + 1 < len(pattern):
                           dep = _get_actual_dep_from_match(parents, pattern, j, ma)
                           feature = feature + ' ' + dep
                        j = j+1
                    yield feature

                    # also add versions where we erase exactly one lemma (this is only generated if specified)
                    if config.NGRAM_WILDCARD:
                        k = 0
                        while k < len(pattern):
                            fs = feature.split(' ')
                            if pattern[k] == '__':
                                fs[k] = '__'
                                yield ' '.join(fs)
                            k = k + 2

    def _find_matches(sentence, mention, tomatch, dicts, parents):
        # TODO compile regex
        '''
        supported tomatch:
        - ANY_LEMMA
        - [cand]
        - [cand:lemma]
        - [subj]
        - [obj]
        - [dic:DICT_NAME]
        x [dic:*]
        '''

        # TODO right now we are neglecting multiple matches
        lemmas = [l.lower() for l in sentence['lemmas']]

        # matches = {pattern : [indexes]}
        matches = {}
        for pattern in tomatch:
            if pattern.startswith('[') and pattern.endswith(']'):
                s = pattern[1:-1]
                if s == 'cand' or s == 'cand:lemma':
                    matches[pattern] = mention.wordidxs
                elif s == 'subj':
                    # Find all subjects
                    matches[pattern] = [i for i in range(len(parents)) \
                        if parents[i][0][0] == 'nsubj' ]
                elif s == 'obj':
                    matches[pattern] = [i for i in range(len(parents)) \
                        if parents[i][0][0] == 'dobj' ]
                elif s == 'dic:*':
                    raise NotImplementedError
                    # Find all indexes that match any dictionary

                    for dic_name in dicts:
                        pattern_name = '[dic:%s]' % dic_name
                        matches[pattern_name] = [i for i in range(len(lemmas)) \
                            if lemmas[i] in dicts[dic_name] ]

                elif s.startswith('dic:'):
                    # Find all indexes that match a specific dictionary
                    dic_name = s[4:]
                    if dic_name not in dicts:
                        print('ERROR: dictionary %s not defined' % dic_name, file=sys.stderr)
                        continue
                    matches[pattern] = [i for i in range(len(lemmas)) \
                        if lemmas[i] in dicts[dic_name] ]
            else:
                # lemma lower match
                matches[pattern] = [i for i in range(len(lemmas)) \
                    if lemmas[i] == pattern ]
                pass

        return matches


    def _featurize_dep_graph(sentence, mention, patterns, parents, children, dicts):

        lemmas = [l.lower() for l in sentence['lemmas']]
        poses = sentence['poses']

        tomatch_set = set()
        tomatch_patterns = []
        for pattern in patterns:
            tomatch = [pattern[i] for i in range(len(pattern)) if i % 2 == 0]
            tomatch_patterns.append(tomatch)
            tomatch_set.update(tomatch)

        # e.g.: {'[dic:young]': [3], '[dic:count]': [], 'cute': [], '[obj]': [], '[dic:girl]': [0], '[dic:negation]': [], '[subj]': [], '[cand]': [3], '[dic:i]': [], '[dic:intensifiers]': [5]}
        matches = _find_matches(sentence, mention, tomatch_set, dicts, parents)

        patterns_found = [pattern for pattern in tomatch_patterns if not any(len(matches[p]) == 0 for p in pattern)]
        # do not compute min path at all, if no pattern found
        if len(patterns_found) == 0:
            return

        min_paths = Dependencies.compute_min_paths(sentence, parents, children, matches, config.MAX_DIST)

        def _get_node_label(pattern, lemma, pos):
            label = lemma
            if pattern.startswith('[dic:'):
                label = pattern

            elif pattern == '[subj]':
                if pos == 'NNP':
                    label = '[subj:NNP]'
                else:
                    label = '[subj:%s]' % lemma
            elif pattern == '[obj]':
                if pos == 'NNP':
                    label = '[obj:NNP]'
                else:
                    label = '[obj:%s]' % lemma
            elif pattern == '[cand]':
                label = '[cand]'
            elif pattern == '[cand0]':
                label = '[cand0]'
            elif pattern == '[cand1]':
                label = '[cand1]'
            elif pattern == '[cand2]':
                label = '[cand2]'
            elif pattern == '[cand:lemma]':
                # A few more clustering
                label = '[cand:%s]' % lemma
                for dic_name in dicts:
                    if lemma in dicts[dic_name]:
                        label = '[cand:dic:%s]' % dic_name
                        break
            return label


        for pattern in tomatch_patterns:
            if any(len(matches[p]) == 0 for p in pattern):
                continue

            feature_complete = True
            feature = ''
            for i in range(len(pattern) - 1):
                k1 = pattern[i]
                if k1 == '[cand:lemma]':
                    k1_lookup = '[cand]'
                else:
                    k1_lookup = k1
                k2 = pattern[i+1]
                if (k1_lookup, k2) not in min_paths:
                    feature_complete = False
                    break
                path, dist, start, end = min_paths[(k1_lookup, k2)]

                label1 = _get_node_label(k1, lemmas[start], poses[start])


                feature += '%s %s ' % (label1, path)

                if i + 1 == len(pattern) - 1: # last pattern

                    label2 = _get_node_label(k2, lemmas[end], poses[end])
                    feature += label2

            if feature_complete:
                yield feature


    def _featurize_others(sentence, mention, patterns, parents, children, dicts):
        if False: yield 'f'

    for mention in mentions:
        sentence = sentence_index[mention.sent_id]['sentence']
        parents = sentence_index[mention.sent_id]['parents']
        children = sentence_index[mention.sent_id]['children']

        # use a set to deduplicate features
        feature_set = set()

        # general, broad-coverage patterns
        if 'NEGATED' in config.feature_patterns:
            for i in mention.wordidxs:
                for c in children[i]:
                    path, child = c
                    if path == 'neg':
                        feature_set.add('NEGATED')
        if 'PLURAL' in config.feature_patterns:
            for i in mention.wordidxs:
                if sentence['poses'][i] == 'NNS':
                    feature_set.add('PLURAL')
        if 'MOD_PLURAL' in config.feature_patterns:
            for i in mention.wordidxs:
                for p in parents[i]:
                    path, parent = p
                    if sentence['poses'][parent] == 'NNS':
                        feature_set.add('MOD_PLURAL')

        patterns = [ pattern for pattern in config.feature_patterns if '_' in pattern]
        for f in _featurize_fixed_length_dependency(sentence, mention, patterns, parents, children, config.dicts):
            feature_set.add(f)

        patterns = [ pattern for pattern in config.feature_patterns if '*' in pattern]
        for f in _featurize_dep_graph(sentence, mention, patterns, parents, children, config.dicts):
            feature_set.add(f)


        patterns = [ pattern for pattern in config.feature_patterns if '_' not in pattern and '*' not in pattern]
        for f in _featurize_others(sentence, mention, patterns, parents, children, config.dicts):
            feature_set.add(f)

        for f in feature_set:
            mention.features.append(f)

    return mentions

def _intersects(a1, a2):
    for i in a1:
        if i in a2:
            return True
    return False

def _acyclic(a):
    return len(a) == len(set(a))


def tsv_dump_mention(m):
    is_correct_str = "\\N"
    if m.is_correct is not None:
        is_correct_str = m.is_correct.__repr__()
    if m.misc is None:
        tsv_line = "\t".join(
            ["\\N", m.doc_id, str(m.sent_id),
                    list_to_tsv_array(m.wordidxs), m.mention_id, m.type,
                    m.entity, list_to_tsv_array(m.words, quote=True),
                    is_correct_str, list_to_tsv_array(list(m.features), True)])
    else:
        tsv_line = "\t".join(
            ["\\N", m.doc_id, str(m.sent_id),
                    list_to_tsv_array(m.wordidxs), m.mention_id, m.type,
                    m.entity, list_to_tsv_array(m.words, quote=True),
                    is_correct_str, list_to_tsv_array(list(m.features), True)]
                    + [tsv_escape(m.misc[k]) for k in m.misc]) # TODO
    return tsv_line

def tsv_escape(value, boolean=False):
    if value is None:
        return '\\N'
    return str(value)

######################################
# Ported from helper/easierlife.py:  #
######################################

def list_to_tsv_array(a_list, quote=False):
    '''
    Convert a list to a string that can be used in a TSV column and intepreted
      as an array by the PostreSQL COPY FROM command.

    If 'quote' is True, then double quote the string representation of the
      elements of the list, and escape double quotes and backslashes.
    '''
    if quote:
        for index in range(len(a_list)):
            if "\\" in str(a_list[index]):
                # Replace '\' with '\\\\"' to be accepted by COPY FROM
                a_list[index] = str(a_list[index]).replace("\\", "\\\\\\\\")
            # This must happen the previous substitution
            if "\"" in str(a_list[index]):
                # Replace '"' with '\\"' to be accepted by COPY FROM
                a_list[index] = str(a_list[index]).replace("\"", "\\\\\"")
        string = ",".join(list(map(lambda x: "\"" + str(x) + "\"", a_list)))
    else:
        string = ",".join(list(map(lambda x: str(x), a_list)))
    return "{" + string + "}"


######################################
# Ported from util/dependencies.py:  #
######################################

class Dependencies:

    def compute_min_paths(sentence, parents, children, index_sets, MAX_DIST=5):
        '''
        Use Floyd-Warshall algorithm to compute shortest paths in dependency tree
        '''
        # print('BEGIN ALGO')
        # print(parents)
        lemmas = sentence['lemmas']

        # Find meaningful nodes
        # nodes = [(index_sets[key], key) for key in index_sets if len(index_sets[key]) > 0]
        N = len(parents)

        clusters = [None] * N
        # Only label it as the first match
        for key in index_sets:
            if key == '[cand:lemma]':
                key = '[cand]'
            if key.startswith('[dic:'):
                for i in index_sets[key]:
                    if clusters[i] is not None:
                        clusters[i] = key
        for i in range(N):
            if clusters[i] is None:
                clusters[i] = lemmas[i]

        # print(clusters)
        INF = 999999
        dist = [INF] * (N * N)
        path = [None] * (N * N)
        for i in range(N):
            dist[i * N + i] = 0
        for i, edges in enumerate(parents):
            for edge in edges:
                label, j = edge
                if label == '': continue
                dist[i * N + j] = 1
                dist[j * N + i] = 1
                # TODO
                path[i * N + j] = '-%s->' % label
                path[j * N + i] = '<-%s-' % label

        for k in range(N):
            for i in range(N):
                if dist[i * N + k] > MAX_DIST:
                    continue
                for j in range(N):
                    if dist[i * N + k] + dist[k * N + j] > MAX_DIST:
                        continue
                    if dist[i * N + j] > dist[i * N + k] + dist[k * N + j]:
                        dist[i * N + j] = dist[i * N + k] + dist[k * N + j]
                        path[i * N + j] = path[i * N + k] + ' %s ' % clusters[k] + path[k * N + j]
                        # print('%d,%d (%d): Update %s -> %s to: %s' % (i, j, dist[i*N+j], clusters[i], clusters[j], path[i*N+j]))

        # print(path)

        # Return results: dependency chain
        result = {}
        for key1 in index_sets:
            idxs1 = index_sets[key1]
            for key2 in index_sets:
                idxs2 = index_sets[key2]
                minpath = None
                mini = minj = None
                mindist = INF
                for i in idxs1:
                    for j in idxs2:
                        if mindist > dist[i * N + j]:
                            mindist = dist[i * N + j]
                            minpath = path[i * N + j]
                            mini, minj = i, j

                if minpath is not None:
                    result[(key1, key2)] = (minpath, mindist, mini, minj)
        # print (result)
        return result


    def min_path_between(sentence, parents, children, indexes_1, indexes_2):
        # TODO BFS / SPFA / Floyed?
        return ''

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

    def match(sentence, path_arr, parents, children, matches, dicts = {}):
        for i in range(0, len(sentence['words'])):
            Dependencies.match_i(sentence, i, path_arr, parents, children, matches, [], dicts)

    def token_match(sentence, i, pw, dicts):
        #w = sentence['words'][i].lower()
        w = sentence['lemmas'][i].lower()
        t = pw.split('|')
        #print(dicts, file=sys.stderr)
        #print('.... checking ' + pw)
        for s in t:
            pair = s.split(':')
            if pair[0] == 'dic':
                if not pair[1] in dicts:
                    print('ERROR: Dictionary ' + pair[1] + ' not found', file=sys.stderr)
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
                print('ERROR: Predicate ' + pair[0] + ' unknown', file=sys.stderr)
                return False
        return True


    def match_i(sentence, i, path_arr, parents, children, matches, matched_prefix = [], dicts = {}):
        if len(path_arr) == 0:
           # nothing to match anymore
           matches.append(matched_prefix)
           return

        pw = path_arr[0]
        # __ is a wildcard matching every word

        matched = False
        if pw == '__':
            matched = True
        elif pw.startswith('[') and pw.endswith(']') and Dependencies.token_match(sentence, i, pw[1:-1], dicts):
            matched = True
        elif sentence['lemmas'][i].lower() == pw:
            matched = True

        if not matched:
           return

        matched_prefix.append(i)
        if len(path_arr) == 1:
            matches.append(matched_prefix)
            return

        # match dep
        pd = path_arr[1]
        if pd[:2] == '<-':
            # left is child
            dep_type = pd[2:-1]
            for p in parents[i]:
                if p[0] == dep_type or dep_type == '__':
                    Dependencies.match_i(sentence, p[1], path_arr[2:], parents, children, matches, list(matched_prefix), dicts)
        elif pd[len(pd)-2:] == '->':
            # left is parent
            dep_type = pd[1:-2]
            for c in children[i]:
                if c[0] == dep_type or dep_type == '__':
                    Dependencies.match_i(sentence, c[1], path_arr[2:], parents, children, matches, list(matched_prefix), dicts)
        elif pd == '_':
            if i+1 < len(sentence['lemmas']):
                Dependencies.match_i(sentence, i+1, path_arr[2:], parents, children, matches, list(matched_prefix), dicts)

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
