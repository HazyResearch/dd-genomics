import ddext
from ddext import SD


def init():
  ddext.input('doc_id', 'text')
  ddext.input('sent_id_1', 'int')
  ddext.input('mention_id_1', 'text')
  ddext.input('wordidxs_1', 'int[]')
  ddext.input('words_1', 'text[]')
  ddext.input('entity_1', 'text')
  ddext.input('type_1', 'text')
  ddext.input('correct_1', 'boolean')
  ddext.input('sent_id_2', 'int')
  ddext.input('mention_id_2', 'text')
  ddext.input('wordidxs_2', 'int[]')
  ddext.input('words_2', 'text[]')
  ddext.input('entity_2', 'text')
  ddext.input('type_2', 'text')
  ddext.input('correct_2', 'boolean')

  ddext.returns('doc_id', 'text')
  ddext.returns('sent_id_1', 'int')
  ddext.returns('sent_id_2', 'int')
  ddext.returns('relation_id', 'text')
  ddext.returns('type', 'text')
  ddext.returns('mention_id_1', 'text')
  ddext.returns('mention_id_2', 'text')
  ddext.returns('wordidxs_1', 'int[]')
  ddext.returns('wordidxs_2', 'int[]')
  ddext.returns('words_1', 'text[]')
  ddext.returns('words_2', 'text[]')
  ddext.returns('entity_1', 'text')
  ddext.returns('entity_2', 'text')
  ddext.returns('is_correct', 'boolean')


def run(doc_id, sent_id_1, mention_id_1, wordidxs_1, words_1, entity_1, mtype_1, correct_1, sent_id_2, mention_id_2, wordidxs_2, words_2, entity_2, mtype_2, correct_2):

  if 'pos_pairs' in SD:
    pos_pairs = SD['pos_pairs']
  else:
    import os
    APP_HOME = os.environ['GDD_HOME']
    pos_pairs = set()
    gpheno = [x.strip().split('\t') for x in open('%s/onto/data/hpo_phenotype_genes.tsv' % APP_HOME)]
    gdisease = [x.strip().split('\t') for x in open('%s/onto/data/hpo_disease_genes.tsv' % APP_HOME)]
    for pheno, gene in gpheno + gdisease:
      pos_pairs.add((gene, pheno))
    SD['pos_pairs'] = pos_pairs

  rid = '%s_%s_g%s_p%s' % (doc_id, sent_id_1, 
    '%d:%d' % (wordidxs_1[0], wordidxs_1[-1]),
    '%d:%d' % (wordidxs_2[0], wordidxs_2[-1]),
    )
  truth = None
  if correct_1 and correct_2:
    gene = entity_1
    for pheno in entity_2.split()[0].split('|'):
      if (gene, pheno) in pos_pairs:
        truth = True
  elif correct_1 is False or correct_2 is False:
    truth = False

  yield (doc_id,
        sent_id_1,
        sent_id_2,
        rid,
        None,
        mention_id_1,
        mention_id_2,
        wordidxs_1,
        wordidxs_2,
        words_1,
        words_2,
        entity_1,
        entity_2,
        truth
        )
