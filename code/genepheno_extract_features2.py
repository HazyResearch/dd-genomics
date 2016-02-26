#! /usr/bin/env python

import collections
import extractor_util as util
import data_util as dutil
import dep_util as deps
import random
import re
import sys
import config

# This defines the Row object that we read in to the extractor
parser = util.RowParser([
            ('relation_id', 'text'),
            ('doc_id', 'text'),
            ('section_id', 'text'),
            ('sent_id', 'int'),
            ('gene_mention_id', 'text'),
            ('gene_name', 'text'),
            ('gene_wordidxs', 'int[]'),
            ('gene_is_correct', 'boolean'),
            ('pheno_mention_id', 'text'),
            ('pheno_entity', 'text'),
            ('pheno_wordidxs', 'int[]'),
            ('pheno_is_correct', 'boolean'),
            ('words', 'text[]'),
            ('lemmas', 'text[]'),
            ('poses', 'text[]'),
            ('ners', 'text[]'),
            ('dep_paths', 'text[]'),
            ('dep_parents', 'int[]')])

# This defines the output Relation object
Feature = collections.namedtuple('Feature', ['doc_id', 'section_id', 'relation_id', 'name'])

HPO_DAG = dutil.read_hpo_dag()

def replace_opts(opts, replaceList):
  ret = {}
  for name in opts:
    strings = opts[name]
    for (pattern, subst) in replaceList:
      if name.endswith('rgx'):
        subst = re.escape(subst)
      strings = [s.replace(pattern, subst) for s in strings]
    ret[name] = strings
  return ret

CACHE = {}

def gp_between(gene_wordidxs, pheno_wordidxs, ners):
  if gene_wordidxs[0] < pheno_wordidxs[0]:
    start = max(gene_wordidxs) + 1
    end = min(pheno_wordidxs) - 1
  else:
    start = max(pheno_wordidxs) + 1
    end = min(gene_wordidxs) - 1
  found_g = False
  found_p = False
  for i in xrange(start, end+1):
    ner = ners[i]
    if ner == 'NERGENE':
      found_g = True
    if ner == 'NERPHENO':
      found_p = True
  return found_g and found_p

def config_supervise(r, row, pheno_entity, gene_name, gene, pheno, 
              phrase, between_phrase, lemma_phrase, between_phrase_lemmas, 
              dep_dag, dep_path_between, gene_wordidxs, VALS, SR):
  if SR.get('phrases-in-between'):
    opts = SR['phrases-in-between']
    orig_opts = opts.copy()
    opts = replace_opts(opts, [('{{G}}', gene), ('{{P}}', pheno)])
    for name, val in VALS:
      if len(opts[name]) + len(opts['%s-rgx' % name]) > 0:
        match = util.rgx_mult_search(between_phrase, opts[name], opts['%s-rgx' % name], orig_opts[name], 
                                     orig_opts['%s-rgx' % name], flags=re.I)
        if match:
          yield r._replace(name='PHRASE_BETWEEN_%s_%s' % (name, non_alnum.sub('_', match)))
        match = util.rgx_mult_search(between_phrase_lemmas, opts[name], opts['%s-rgx' % name], 
                                     orig_opts[name], orig_opts['%s-rgx' % name], flags=re.I)
        if match:
          yield r._replace(name='PHRASE_BETWEEN_%s_%s' % (name, non_alnum.sub('_', match)))

  if SR.get('phrases-in-sent'):
    opts = SR['phrases-in-sent']
    orig_opts = opts.copy()
    opts = replace_opts(opts, [('{{G}}', gene), ('{{P}}', pheno)])
    for name, val in VALS:
      if len(opts[name]) + len(opts['%s-rgx' % name]) > 0:
        match = util.rgx_mult_search(phrase, opts[name], opts['%s-rgx' % name], orig_opts[name], 
                                     orig_opts['%s-rgx' % name], flags=re.I)
        if match:
          yield r._replace(name='PHRASE_%s_%s' % (name, non_alnum.sub('_', match)))
        match = util.rgx_mult_search(lemma_phrase, opts[name], opts['%s-rgx' % name], orig_opts[name], 
                                     orig_opts['%s-rgx' % name], flags=re.I)
        if match:
          yield r._replace(name='PHRASE_%s_%s' % (name, non_alnum.sub('_', match)))

  if SR.get('primary-verb-modifiers') and dep_dag:
    opts = SR['primary-verb-modifiers']
    if dep_path_between:
      verbs_between = [i for i in dep_path_between if row.poses[i].startswith("VB")]
      if len(verbs_between) > 0:
        for name, val in VALS:
          mod_words = [i for i, x in enumerate(row.lemmas) if x in opts[name]]
          mod_words += [i for i, x in enumerate(row.dep_paths) if x in opts['%s-dep-tag' % name]]
          d = dep_dag.path_len_sets(verbs_between, mod_words)
          if d and d < opts['max-dist'] + 1:
            subtype = 'ModWords: ' + ' '.join([str(m) for m in mod_words]) + ', VerbsBetween: ' + ' '.join([str(m) for m in verbs_between]) + ', d: ' + str(d)
            yield r._replace(name='PRIMARY_VB_MOD_%s_%s' % (name, non_alnum.sub('_', subtype)))

  if SR.get('dep-lemma-connectors') and dep_dag:
    opts = SR['dep-lemma-connectors']
    for name, val in VALS:
      if dep_path_between:
        connectors = [i for i, x in enumerate(row.lemmas) \
                      if i in dep_path_between and x in opts[name]]
        if len(connectors) > 0:
          yield r._replace(name='DEP_LEMMA_CONNECT_%s_%s' % (name, non_alnum.sub('_', 
                                  ' '.join([str(x) for x in connectors]))))

  if SR.get('dep-lemma-neighbors') and dep_dag:
    opts = SR['dep-lemma-neighbors']
    for name, val in VALS:
      for entity in ['g', 'p']:
        lemmas = [i for i, x in enumerate(row.lemmas) if x in opts['%s-%s' % (name, entity)]]
        d = dep_dag.path_len_sets(gene_wordidxs, lemmas)
        if d and d < opts['max-dist'] + 1:
          subtype = ' '.join([str(l) for l in lemmas]) + ', d: ' + str(d)
          yield r._replace(name='DEP_LEMMA_NB_%s_%s_%s' % (name, 
                                                           entity, 
                                                           non_alnum.sub('_', subtype)))
  
  if ('neg', False) in VALS:
    if gp_between(row.gene_wordidxs, row.pheno_wordidxs, row.ners):
      yield r._replace(name='NEG_GP_BETWEEN')
  
  yield r._replace(name='DEFAULT_FEATURE')

non_alnum = re.compile('[\W_]+')
def create_supervised_relation(row, SR, HF):
  gene_wordidxs = row.gene_wordidxs
  gene_is_correct = row.gene_is_correct
  pheno_entity = row.pheno_entity
  pheno_wordidxs = row.pheno_wordidxs
  pheno_is_correct = row.pheno_is_correct
  gene = row.gene_name
  pheno = ' '.join([row.words[i] for i in row.pheno_wordidxs])

  phrase = ' '.join(row.words)
  lemma_phrase = ' '.join(row.lemmas)
  b = sorted([gene_wordidxs[0], gene_wordidxs[-1], pheno_wordidxs[0], pheno_wordidxs[-1]])[1:-1]
  assert b[0] + 1 < len(row.words), str((b[0] + 1, len(row.words), row.doc_id, row.section_id, row.sent_id, str(row.words)))
  assert b[1] < len(row.words), str((b[1], len(row.words), row.doc_id, row.section_id, row.sent_id, str(row.words)))
  between_phrase = ' '.join(row.words[i] for i in range(b[0] + 1, b[1]))
  between_phrase_lemmas = ' '.join(row.lemmas[i] for i in range(b[0] + 1, b[1]))

  dep_dag = deps.DepPathDAG(row.dep_parents, row.dep_paths, row.words, max_path_len=HF['max-dep-path-dist'])
  
  r = Feature(row.doc_id, row.section_id, row.relation_id, None)
  path_len_sets = dep_dag.path_len_sets(gene_wordidxs, pheno_wordidxs)
  if not path_len_sets:
    if SR.get('bad-dep-paths'):
      yield r._replace(name='BAD_OR_NO_DEP_PATH')

  dep_path_between = dep_dag.min_path_sets(gene_wordidxs, pheno_wordidxs) if dep_dag else None

  if SR.get('g-or-p-false'):
    if gene_is_correct == False or pheno_is_correct == False:
      yield r._replace(name='G_ANDOR_P_FALSE_%s_%s' % (str(gene_is_correct), str(pheno_is_correct)))

  if SR.get('adjacent-false'):
    if re.search(r'[a-z]{3,}', between_phrase, flags=re.I) is None:
      st = non_alnum.sub('_', between_phrase)
      yield r._replace(name='G_P_ADJACENT_%s' % st)

  gene_name = row.gene_name

  VALS = [('neg', False)]
  for rv in config_supervise(r, row, pheno_entity, gene_name, gene, pheno, 
              phrase, between_phrase, \
              lemma_phrase, between_phrase_lemmas, dep_dag, \
              dep_path_between, gene_wordidxs, 
              VALS, SR):
    yield rv
  
  VALS = [('pos', True)]
  for rv in config_supervise(r, row, pheno_entity, gene_name, gene, pheno, 
              phrase, between_phrase, \
              lemma_phrase, between_phrase_lemmas, dep_dag, \
              dep_path_between, gene_wordidxs, 
              VALS, SR):
    yield rv

def featurize(supervision_rules, hard_filters):
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)
    for rv in create_supervised_relation(row, SR=supervision_rules, HF=hard_filters):
      util.print_tsv_output(rv)

if __name__ == '__main__':
  sr = config.GENE_PHENO_CAUSATION['SR']
  hf = config.GENE_PHENO_CAUSATION['HF']
  featurize(sr, hf)
