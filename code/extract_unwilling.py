#! /usr/bin/env python3

# extract_underage.py
#
# Input:  [doc_id, words, sent_ids]
# Output: [doc_id, sent_id, start_position, length, text, mention_id]
#

from util import dependencies
import fileinput
import sys
import os
import re
import json
import random
import collections
from helper.easierlife import BASE_DIR, list_to_tsv_array

path = BASE_DIR + '/data/dicts/common_words.tsv'

stopwords = frozenset([line.strip().lower() for line in open(path)])

Document = collections.namedtuple('Document', ['doc_id', 'text', 'words', 'lemmas', 'poses', 'dep_paths', 'dep_parents'])
Mention = collections.namedtuple('Mention', ['doc_id', 'sent_id', 'wordidxs', 'mention_id', 'type', 'entity', 'words', 'is_correct', 'features'])



dicts = {
  'intensifiers' : [
    'very',
    'really',
    'extremely',
    'amazingly',
    'exceptionally',
    'incredibly',
    'unusually',
    'remarkably',
    'particularly',
    'absolutely',
    'completely',
    'totally',
    'utterly',
    'quite',
    'definitely',
    'too',
    'so',
    'super'
  ],
  'disintensifiers' : [
    'little',
    'bit',
    'slightly',
    'somewhat',
    'pretty'
  ],
  'profession' : [
    'job',
    'profession',
    'sex',
    'business',
    'game',
    'trade',
    'occupation',
    'career'
  ],
  'bad' : [
    'bad',
    'awful',
    'lousy',
    'poor',
    'terrible'
  ],
  'good' : [
    'good',
    'great',
    'amazing',
    'terrific'
  ],
  'disinterest' : [
    'uninterested',
    'mechanical',
    'impersonal',
    'lifeless',
    'emotionless',
    'involuntary',
    'monotonous',
    'indifferent',
    'unfriendly',
    'apathetic',
    'disinterested',
    'uninvolved',
    'bored',
    'distant',
    'forced',
    'rushed',
    'unwilling',
    'annoyed',
    'bitter',
    'irritated',
    'resentful',
    'uptight',
    'agitated',
    'troubled'
    #'cold'
  ],
  'interest' : [
    'enthusiastic',
    'eager',
    'vigorous',
    'warm',
    'passionate',
    'pleasant',
    #'willing',
    'exhilarated',
    'lively',
  ],
  'interest_verbs' : [
    'enjoy',
    'adore',
    'dig',
    'love'
  ],
  'name' : [
  ],
  'lady' : [
    'lady',
    'woman',
    'girl',
    'blonde',
    'ebony',
    'gal',
    'girl',
    'slut',
    'cutie',
    'hottie',
    'she',
    'her',
  ],
  'positive_words' : [
    'amazing',
    'nice',
    'talented',
    'awesome',
    'sweetheart'
  ]
}


candidate_patterns = [
  '[dic:disinterest]',
  '[dic:interest]',
  '[dic:interest_verbs]',
  'attitude',
  '[dic:positive_words]',
  'be -prep_into-> it',
  'be -prep_into-> this'
]

pos_patterns = [
    '[dic:lady] <-nsubj- [dic:disinterest] -advmod-> [dic:intensifiers]',
    '[dic:lady] <-nsubj- [dic:interest] -neg-> not',
    '[dic:lady] <-nsubj- attitude -amod-> [dic:bad]',
    'attitude <-nsubj- [dic:bad]',
    'not <-neg- [dic:interest_verbs] -__-> [dic:profession]'
]

candidate_phrases = [
]

pos_phrases = [
    'she is not into it',
    "she 's not into it",
    "she 's not into this",
    'she is not into this'
]

neg_patterns = [
    '[dic:lady] <-nsubj- [dic:interest]',
    '[dic:lady] <-nsubj- [dic:disinterest] -neg-> not',
    'attitude <-nsubj- [dic:bad] -neg-> not',
    'attitude <-nsubj- [dic:good]',
    '[dic:good] <-amod- attitude',
    'i <-nsubj- [dic:interest_verbs]',
    'i <-nsubj- [dic:interest] -neg-> not',
    'i <-nsubj- [dic:disinterest] -advmod-> [dic:intensifiers]',
    '[dic:lady] <-nsubj- [dic:interest_verbs]',
    '[dic:lady] <-nsubj- [dic:positive_words]',
    '[dic:lady] -amod-> [dic:positive_words]',
    '[dic:lady] <-nsubj- [dic:disinterest] -advmod-> [dic:disintensifiers]'
]

neg_phrases = [
    'she is into it',
    'she was into it',
    'she was really into it',
    'she was extremely into it',
    'she was definitely into it',
    'she is into this'
]

neg_phrases = [
]

feature_patterns = [
    '[dic:lady] <-nsubj- __ -__-> __',
    '[dic:lady] _ __ _ __',
    '__ _ [dic:lady] _ __',
    '__ _ __ _ [dic:lady]',
    '[dic:lady] _ __ _ __ _ __',
    '__ _ [dic:lady] _ __ _ __',
    '__ _ __ _ [dic:lady] _ __',
    '__ _ __ _ __ _ [dic:lady]'
]

bad_features = [
    'she _ be _ not'
]

# PATERNS IN OUR DIST SUP:
#__ <-__- XX
#__ <-__- __ -__-> XX
#__ _ XX
#__ _ XX _ XX
#__ XX __
#__ -__-> XX
#__ <-__- XX -__-> __
#__ _ __ _ __ _ __ _ XX
#XX <-__- [] -__-> __



pos_dep_patterns = [ p.split(' ') for p in pos_patterns ]
neg_dep_patterns = [ p.split(' ') for p in neg_patterns ]
candidate_dep_patterns = [ p.split(' ') for p in candidate_patterns ]

for i in dicts:
    dicts[i] = frozenset(dicts[i])

for i in range(0, len(feature_patterns)):
    feature_patterns[i] = feature_patterns[i].split(' ')

def index_of_sublist(subl, l):
    for i in range(len(l) - len(subl) + 1):
        if subl == l[i:i+len(subl)]:
            return i

def supervise(mentions, sentence_index, doc):
    n_mentions = []

    # mentions by sent_id
    sent_mentions = {}
    for m in mentions:
        l = sent_mentions.get(m.sent_id, [])
        l.append(m)
        sent_mentions[m.sent_id] = l

    for sent_num in range(0, len(sentence_index)):
        sentence = sentence_index[sent_num]['sentence']
        parents = sentence_index[sent_num]['parents']
        children = sentence_index[sent_num]['children']
        sm = sent_mentions.get(sent_num, [])
        if len(sm) == 0:
            continue

        labeling = {}
        for m in sm:
            labeling[id(m)] = None

        for p in pos_phrases:
            start = index_of_sublist(p, sentence['words'])
            if start is not None:
                match_indices = range(start, start+len(p))
                for m in mentions:
                    if intersects(match_indices, m.wordidxs):
                        labeling[id(m)] = True

        for p in pos_dep_patterns:
            matches = []
            dependencies.match(sentence, p, parents, children, matches, dicts)
            for ma in matches:
                for m in sm:
                    if intersects(ma, m.wordidxs):
                        labeling[id(m)] = True

        for p in neg_dep_patterns:
            matches = []
            dependencies.match(sentence, p, parents, children, matches, dicts)
            for ma in matches:
                for m in sm:
                    if intersects(ma, m.wordidxs):
                        if labeling[id(m)] is None:
                            labeling[id(m)] = False
        for m in sm:
            l = labeling[id(m)]
            n_mentions.append(m._replace(is_correct = l))

    return n_mentions


def featurize(mentions, sentence_index, doc):
    for m in mentions:
        sentence = sentence_index[m.sent_id]['sentence']
        parents = sentence_index[m.sent_id]['parents']
        children = sentence_index[m.sent_id]['children']

        feature_set = set()

        # find dependency path that covers wordidxs, lemmatize

        #feature = ''
        #for i in m.wordidxs:
        #    m.features.append(sentence['lemmas'][i])
        #    for p in parents[i]:
        #        path, parent = p
        #        if parent in m.wordidxs:
        #            feature = feature + sentence['lemmas'][i] + '<-' + path + '-' + sentence['lemmas'][parent] + '|||'

        #if feature != '':
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
            edge_pattern = pattern[2*j + 1]
            if edge_pattern[:2] == '<-':
                #print(str(ma[j]), file=sys.stderr)
                #print(str(parents[ma[j]]), file=sys.stderr)
                dep = '<-' + parents[ma[j]][0][0] + '-'
            elif edge_pattern[len(edge_pattern)-2:] == '->':
                dep = '-' + parents[ma[j+1]][0][0] + '->'
            elif edge_pattern == '_':
                dep = '_'
            else:
                print('ERROR: Unknown edge pattern', file=sys.stderr)
            return dep

        #pattern = '__ <-prep_like- __ -nsubj-> __'.split(' ')
        #for pattern in feature_patterns:
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

        #pattern = '__ <-prep_like- __ -nsubj-> __'.split(' ')
        for pattern in feature_patterns:
            matches = []
            dependencies.match(sentence, pattern, parents, children, matches, dicts)
            for ma in matches:
                if intersects(m.wordidxs, ma) and acyclic(ma):
                    #feature = '__' + pattern[1]
                    feature = sentence['lemmas'][ma[0]] + ' ' + get_actual_dep_from_match(pattern, 0, ma)
                    j = 1
                    while j < len(ma):
                        feature = feature + ' ' + sentence['lemmas'][ma[j]]
                        if 2*j + 1 < len(pattern):
                            dep = get_actual_dep_from_match(pattern, j, ma)
                            feature = feature + ' ' + dep
                        j = j+1
                    feature_set.add(feature)

        for f in feature_set:
          if f in bad_features:
            continue
          m.features.append(feature_prefix + '_' + f)
    return mentions

def intersects(a1, a2):
    for i in a1:
        if i in a2:
            return True
    return False

def acyclic(a):
    return len(a) == len(set(a))

def extract_candidates(sentence_index, doc):
    mentions = []
    sent_token_offset = 0

    for sent_num in range(0, len(sentence_index)):
        sentence = sentence_index[sent_num]['sentence']
        parents = sentence_index[sent_num]['parents']
        children = sentence_index[sent_num]['children']

        # match dependency patterns
        mention_num = 0

        for p in candidate_dep_patterns:
            matches = []
            dependencies.match(sentence, p, parents, children, matches, dicts)
            for m in matches:
                mention = Mention(
                    doc_id = doc.doc_id,
                    sent_id = sent_num,
                    #wordidxs = [ sent_token_offset + i for i in m],
                    wordidxs = m,
                    mention_id = doc.doc_id + '_' + str(sent_num) + '_' + str(mention_num),
                    type = '',
                    entity = ' '.join([ sentence['lemmas'][i] for i in m ]),
                    words = [ sentence['words'][i] for i in m ],
                    is_correct = None,
                    features = []
                )
                mentions.append(mention)
                mention_num = mention_num + 1
        sent_token_offset = sent_token_offset + len(sentence['words'])
    return mentions

def create_sentence_index(doc):
    index = []
    for sent_num in range(0, len(doc.words)):
        sentence = {
            'words' : doc.words[sent_num],
            'lemmas' : doc.lemmas[sent_num],
            'poses' : doc.poses[sent_num],
            'dep_paths' : doc.dep_paths[sent_num],
            'dep_parents' : [ p-1 for p in doc.dep_parents[sent_num]]
        }
        parents, children = dependencies.build_indexes(sentence)
        index.append({
            'sentence': sentence,
            'parents': parents,
            'children': children
        })
    return index

def tsv_dump_mention(m):
    is_correct_str = "\\N"
    if m.is_correct is not None:
        is_correct_str = m.is_correct.__repr__()
    tsv_line = "\t".join(
        ["\\N", m.doc_id, str(m.sent_id),
                list_to_tsv_array(m.wordidxs), m.mention_id, m.type,
                m.entity, list_to_tsv_array(m.words, quote=True),
                is_correct_str, list_to_tsv_array(list(m.features), True)])
    return tsv_line

def convert_nlp_to_legacy_format(line):
    t = line.rstrip('\n').split('\t')
    # convert deps into dep_paths and dep_parents
    doc_tokens = json.loads(t[2])
    doc_lemmas = json.loads(t[3])
    doc_poses = json.loads(t[4])
    doc_sent_tok_offsets = json.loads(t[5])
    num_sents = len(doc_sent_tok_offsets)
    doc_deps = json.loads(t[6])
    doc_dep_paths = []
    doc_dep_parents = []
    doc_sent_tokens = []
    doc_sent_lemmas = []
    doc_sent_poses = []
    for i in range(0, num_sents):
        tok_begin = doc_sent_tok_offsets[i][0]
        tok_end = doc_sent_tok_offsets[i][1]
        num_toks = tok_end - tok_begin
        dep_paths = ['']*num_toks
        dep_parents = [0]*num_toks
        for d in doc_deps[i]:
            dep_paths[d['to']] = d['name']
            dep_parents[d['to']] = d['from']+1
        doc_dep_paths.append(dep_paths)
        doc_dep_parents.append(dep_parents)
        doc_sent_tokens.append(doc_tokens[tok_begin:tok_end])
        doc_sent_lemmas.append(doc_lemmas[tok_begin:tok_end])
        doc_sent_poses.append(doc_poses[tok_begin:tok_end])

    doc = Document(
        doc_id = t[0],
        text = json.loads(t[1].replace('\\\\', '\\')),
        words = doc_sent_tokens,
        lemmas = doc_sent_lemmas,
        poses = doc_sent_poses,
        dep_paths = doc_dep_paths,
        dep_parents = doc_dep_parents)
    return doc

if __name__ == "__main__":
    # Process the input
    with fileinput.input() as input_files:
        for line in input_files:
            doc = convert_nlp_to_legacy_format(line)

            sentence_index = create_sentence_index(doc)
            mentions = extract_candidates(sentence_index, doc)
            mentions = featurize(mentions, sentence_index, doc)
            mentions = supervise(mentions, sentence_index, doc)

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

