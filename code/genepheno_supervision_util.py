import collections
import extractor_util as util
import data_util as dutil
import dep_util as deps
import os
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
            ('gene_entity', 'text'),
            ('gene_wordidxs', 'int[]'),
            ('gene_is_correct', 'boolean'),
            ('pheno_mention_id', 'text'),
            ('pheno_entity', 'text'),
            ('pheno_wordidxs', 'int[]'),
            ('pheno_is_correct', 'boolean'),
            ('words', 'text[]'),
            ('lemmas', 'text[]'),
            ('poses', 'text[]'),
            ('dep_paths', 'text[]'),
            ('dep_parents', 'int[]')])

# This defines the output Relation object
Relation = collections.namedtuple('Relation', [
            'dd_id',
            'relation_id',
            'doc_id',
            'section_id',
            'sent_id',
            'gene_mention_id',
            'gene_entity',
            'gene_wordidxs',
            'pheno_mention_id',
            'pheno_entity',
            'pheno_wordidxs',
            'is_correct',
            'relation_supertype',
            'relation_subtype'])

EID_MAP = dutil.gene_symbol_to_ensembl_id_map()
HPO_DAG = dutil.read_hpo_dag()

def read_supervision():
  """Reads genepheno supervision data (from charite)."""
  supervision_pairs = set()
  with open('%s/onto/data/canon_phenotype_to_gene.map' % util.APP_HOME) as f:
    for line in f:
      hpo_id, gene_symbol = line.strip().split('\t')
      hpo_ids = [hpo_id] + [parent for parent in HPO_DAG.edges[hpo_id]]
      eids = EID_MAP[gene_symbol]
      for h in hpo_ids:
        for e in eids:
          supervision_pairs.add((h,e))
  return supervision_pairs

# count_g_or_p_false_none = 0 
# count_adjacent_false_none = 0 

def create_supervised_relation(row, superv_diff, SR, HF, charite_pairs):
  """
  Given a Row object with a sentence and several gene and pheno objects, create and 
  supervise a Relation output object for the ith gene and jth pheno objects
  Note: outputs a list for convenience
  Also includes an input for d = pos - neg supervision count, for neg supervision
  """
  gene_mention_id = row.gene_mention_id
  gene_entity = row.gene_entity
  gene_wordidxs = row.gene_wordidxs
  gene_is_correct = row.gene_is_correct
  pheno_mention_id = row.pheno_mention_id
  pheno_entity = row.pheno_entity
  pheno_wordidxs = row.pheno_wordidxs
  gene_is_correct = row.gene_is_correct
  pheno_is_correct = row.pheno_is_correct

  phrase = ' '.join(row.words)
  lemma_phrase = ' '.join(row.lemmas)
  b = sorted([gene_wordidxs[0], gene_wordidxs[-1], pheno_wordidxs[0], pheno_wordidxs[-1]])[1:-1]
  between_phrase = ' '.join(row.words[i] for i in range(b[0]+1,b[1]))
  between_phrase_lemmas = ' '.join(row.lemmas[i] for i in range(b[0]+1,b[1]))

  # Create a dependencies DAG for the sentence
  dep_dag = deps.DepPathDAG(row.dep_parents, row.dep_paths, row.words, max_path_len=HF['max-dep-path-dist'])

  relation_id = '%s_%s' % (gene_mention_id, pheno_mention_id)
  r = Relation(None, relation_id, row.doc_id, row.section_id, row.sent_id, gene_mention_id, gene_entity, \
               gene_wordidxs, pheno_mention_id, pheno_entity, pheno_wordidxs, None, None, None)
  path_len_sets = dep_dag.path_len_sets(gene_wordidxs, pheno_wordidxs)
  if not path_len_sets:
    if SR.get('bad-dep-paths'):
      return r._replace(is_correct=False, relation_supertype='BAD_OR_NO_DEP_PATH')
    else:
      return None

  dep_path_between = frozenset(dep_dag.min_path_sets(gene_wordidxs, pheno_wordidxs)) if dep_dag else None
  
  # distant supervision rules & hyperparameters
  # NOTE: see config.py for all documentation & values

  # global count_g_or_p_false_none
  # global count_adjacent_false_none
  
  if SR.get('g-or-p-false'):
    opts = SR['g-or-p-false']
    # The following line looks like it was written by a prosimian, but it is actually correct.
    # Do not mess with the logic unless you know what you're doing.
    # (Consider that Boolean variables can and will take the value ``None'' in this language.)
    if not (gene_is_correct != False and pheno_is_correct != False):
      if random.random() < opts['diff']*superv_diff or random.random() < opts['rand']:
        return r._replace(is_correct=False, relation_supertype='G_ANDOR_P_FALSE', relation_subtype='gene_is_correct: %s, pheno_is_correct: %s' % (gene_is_correct, pheno_is_correct))
      else:
        # count_g_or_p_false_none += 1
        return None

  if SR.get('adjacent-false'):
    if re.search(r'[a-z]{3,}', between_phrase, flags=re.I) is None:
      if random.random() < 0.5*superv_diff or random.random() < 0.01:
        return r._replace(is_correct=False, relation_supertype='G_P_ADJACENT', relation_subtype=between_phrase)
      else:
        # count_adjacent_false_none += 1
        return None

  VALS = config.GENE_PHENO['vals']
  if SR.get('phrases-in-sent'):
    opts = SR['phrases-in-sent']
    for name,val in VALS:
      if len(opts[name]) + len(opts['%s-rgx' % name]) > 0:
        match = util.rgx_mult_search(phrase + ' ' + lemma_phrase, opts[name], opts['%s-rgx' % name], flags=re.I)
        if match:
          return r._replace(is_correct=val, relation_supertype='PHRASE_%s' % name, relation_subtype=match)

  if SR.get('phrases-in-between'):
    opts = SR['phrases-in-between']
    for name,val in VALS:
      if len(opts[name]) + len(opts['%s-rgx' % name]) > 0:
        match = util.rgx_mult_search(between_phrase + ' ' + between_phrase_lemmas, opts[name], opts['%s-rgx' % name], flags=re.I)
        if match:
          return r._replace(is_correct=val, relation_supertype='PHRASE_BETWEEN_%s' % name, relation_subtype=match)

  if SR.get('primary-verb-modifiers') and dep_dag:
    opts = SR['primary-verb-modifiers']
    if dep_path_between:
      verbs_between = [i for i in dep_path_between if row.poses[i].startswith("VB")]
      if len(verbs_between) > 0:
        for name,val in VALS:
          mod_words = [i for i,x in enumerate(row.lemmas) if x in opts[name]]
          mod_words += [i for i,x in enumerate(row.dep_paths) if x in opts['%s-dep-tag' % name]]
          d = dep_dag.path_len_sets(verbs_between, mod_words)
          if d and d < opts['max-dist'] + 1:
            subtype = 'ModWords: ' + ' '.join([str(m) for m in mod_words]) + ', VerbsBetween: ' + ' '.join([str(m) for m in verbs_between]) + ', d: ' + str(d)
            return r._replace(is_correct=val, relation_supertype='PRIMARY_VB_MOD_%s' % name, relation_subtype=subtype)

  if SR.get('dep-lemma-connectors') and dep_dag:
    opts = SR['dep-lemma-connectors']
    for name,val in VALS:
      if dep_path_between:
        connectors = [i for i,x in enumerate(row.lemmas) if i in dep_path_between and x in opts[name]]
        if len(connectors) > 0:
          return r._replace(is_correct=val, relation_supertype='DEP_LEMMA_CONNECT_%s' % name, relation_subtype=' '.join([str(c) for c in connectors]))

  if SR.get('dep-lemma-neighbors') and dep_dag:
    opts = SR['dep-lemma-neighbors']
    for name,val in VALS:
      for entity in ['g','p']:
        lemmas = [i for i,x in enumerate(row.lemmas) if x in opts['%s-%s' % (name,entity)]]
        d = dep_dag.path_len_sets(gene_wordidxs, lemmas)
        if d and d < opts['max-dist'] + 1:
          subtype = ' '.join([str(l) for l in lemmas]) + ', d: ' + str(d)
          return r._replace(is_correct=val, relation_supertype='DEP_LEMMA_NB_%s_%s' % (name,entity), relation_subtype=subtype)

  if SR.get('charite-all-pos'):
    if (pheno_entity, gene_entity) in charite_pairs:
      return r._replace(is_correct=True, relation_supertype='CHARITE_SUP') 

  # Return GP relation object
  return r

def supervise(supervision_rules, hard_filters):
  # generate the mentions, while trying to keep the supervision approx. balanced
  # print out right away so we don't bloat memory...
  pos_count = 0
  neg_count = 0
  # load in static data
  CHARITE_PAIRS = read_supervision()
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)

    relation = create_supervised_relation(row, superv_diff=pos_count-neg_count, SR=supervision_rules, HF=hard_filters, charite_pairs=CHARITE_PAIRS)
    
    if relation:
      if relation.is_correct == True:
        pos_count += 1
      elif relation.is_correct == False:
        neg_count += 1
      util.print_tsv_output(relation)
  # sys.stderr.write('count_g_or_p_false_none: %s\n' % count_g_or_p_false_none)
  # sys.stderr.write('count_adjacent_false_none: %s\n' % count_adjacent_false_none)

