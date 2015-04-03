import ddext
from ddext import SD


def init():
  ddext.input('doc_id', 'text')
  ddext.input('sent_id', 'int')
  ddext.input('words', 'text[]')
  ddext.input('lemmas', 'text[]')
  ddext.input('poses', 'text[]')
  ddext.input('ners', 'text[]')

  ddext.returns('doc_id', 'text')
  ddext.returns('sent_id', 'int')
  ddext.returns('wordidxs', 'int[]')
  ddext.returns('mention_id', 'text')
  ddext.returns('type', 'text')
  ddext.returns('entity', 'text')
  ddext.returns('words', 'text[]')
  ddext.returns('is_correct', 'boolean')


def run(doc_id, sent_id, words, lemmas, poses, ners):

  if 'diseases' in SD:
    trie = SD['trie']
    diseases = SD['diseases']
    diseases_bad = SD['diseases_bad']
    genes = SD['genes']
    delim_re = SD['delim_re']
  else:
    import os
    APP_HOME = os.environ['DD_GENOMICS_HOME']
    import re
    diseases = {}
    all_diseases = [x.strip().split('\t', 1) for x in open('%s/onto/data/all_diseases.tsv' % APP_HOME)]
    diseases_en = set([x.strip() for x in open('%s/onto/data/all_diseases_en.tsv' % APP_HOME)])
    diseases_en_good = set([x.strip() for x in open('%s/onto/manual/disease_en_good.tsv' % APP_HOME)])
    diseases_bad = set([x.strip() for x in open('%s/onto/manual/disease_bad.tsv' % APP_HOME)])
    SD['diseases_bad'] = diseases_bad

    diseases_exclude = diseases_bad | diseases_en - diseases_en_good
    delim_re = re.compile('[^\w-]+')  # NOTE: this also removes apostrophe
    SD['delim_re'] = delim_re
    diseases_norm = {}

    trie = {}  # special key '$' means terminal nodes

    for phrase, ids in all_diseases:
      if phrase in diseases_exclude:
        continue
      diseases[phrase] = ids
      phrase_norm = delim_re.sub(' ', phrase).strip()
      # print phrase_norm
      tokens = phrase_norm.split()
      node = trie
      for w in tokens:
        if w not in node:
          node[w] = {}
        node = node[w]
      if '$' not in node:
        node['$'] = []
      node['$'].append((ids, phrase))
      if phrase_norm not in diseases_norm:
        diseases_norm[phrase_norm] = ids
      else:
        diseases_norm[phrase_norm] = '|'.join(sorted(set(ids.split('|')) | set(diseases_norm[phrase_norm].split('|'))))

    SD['diseases'] = diseases
    SD['trie'] = trie

    genes = set()
    for line in open('%s/onto/data/genes.tsv' % APP_HOME):
      #plpy.info(line)
      name, synonyms, full_names = line.strip(' \r\n').split('\t')
      synonyms = set(synonyms.split('|'))
      genes.add(name.lower())
      for s in synonyms:
        genes.add(s.lower())

    SD['genes'] = genes

  # TODO: currently we do ignore-case exact match for single words; consider stemming.
  # TODO: currently we do exact phrase matches; consider emitting partial matches.
  for i in xrange(len(words)):
    word = words[i]
    iword = word.lower()

    # single-token mention
    if iword in diseases:
      truth = True
      mtype = 'ONE'

      # http://www.ncbi.nlm.nih.gov/pubmed/23271346
      # SCs for Stem Cells
      # HFs for hair follicles
      if word[-1] == 's' and word[:-1].isupper():
        truth = False
        mtype = 'PLURAL'
      elif iword in genes:
        truth = None
        mtype = 'GSYM'

      entity = diseases[iword] + ' ' + iword
      mid = '%s_%s_%d_1' % (doc_id, sent_id, i)
      yield doc_id, sent_id, [i], mid, mtype, entity, [word], truth

    # multi-token mentions
    node = trie
    depth = 0
    for j in xrange(i, len(words)):
      word = words[j]
      iword = word.lower()
      sword = delim_re.sub(' ', iword).strip()
      if not sword:
        if j == i:
          break
        continue
      if sword in node:
        node = node[sword]
        depth += 1
        if '$' in node and depth > 1:
          for ids, phrase in node['$']:
            if phrase in diseases_bad:
              continue
            entity = ids + ' ' + phrase
            mid = '%s_%s_%d_%d' % (doc_id, sent_id, i, j - i + 1)
            wordids = range(i, j + 1)
            yield doc_id, sent_id, wordids, mid, 'PHRASE', entity, words[i: j + 1], True
      else:
        break

