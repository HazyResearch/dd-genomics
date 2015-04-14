import ddext

def init():
  ddext.input('doc_id', 'text')
  ddext.input('sent_id', 'int')
  ddext.input('words', 'text[]')
  ddext.input('lemmas', 'text[]')
  ddext.input('poses', 'text[]')
  ddext.input('ners', 'text[]')
  ddext.input('dep_paths', 'text[]')
  ddext.input('dep_parents', 'int[]')
  ddext.input('wordidxs', 'int[]')
  ddext.input('relation_id', 'text')
  ddext.input('wordidxs_1', 'int[]')
  ddext.input('wordidxs_2', 'int[]')

  ddext.returns('doc_id', 'text')
  ddext.returns('relation_id', 'text')
  ddext.returns('feature', 'text')


def run(doc_id, sent_id, words, lemmas, poses, ners, dep_paths, dep_parents, wordidxs, relation_id, wordidxs_1, wordidxs_2):
  try:
    import ddlib
  except:
    import os
    DD_HOME = os.environ['DEEPDIVE_HOME']
    from sys import path
    path.append('%s/ddlib' % DD_HOME)
    import ddlib

  obj = dict()
  obj['lemma'] = []
  obj['words'] = []
  obj['ner'] = []
  obj['pos'] = []
  obj['dep_graph'] = []
  for i in xrange(len(words)):
      obj['lemma'].append(lemmas[i])
      obj['words'].append(words[i])
      obj['ner'].append(ners[i])
      obj['pos'].append(poses[i])
      obj['dep_graph'].append(
          str(int(dep_parents[i])) + "\t" + dep_paths[i] + "\t" + str(i))
  word_obj_list = ddlib.unpack_words(
      obj, lemma='lemma', pos='pos', ner='ner', words='words', dep_graph='dep_graph')
  gene_span = ddlib.get_span(wordidxs_1[0], len(wordidxs_1))
  pheno_span = ddlib.get_span(wordidxs_2[0], len(wordidxs_2))
  features = set()
  for feature in ddlib.get_generic_features_relation(word_obj_list, gene_span, pheno_span):
    features.add(feature)
  for feature in features:
    yield doc_id, relation_id, feature

