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
  ddext.input('mention_id', 'text')
  ddext.input('wordidxs', 'int[]')

  ddext.returns('doc_id', 'text')
  ddext.returns('mention_id', 'text')
  ddext.returns('feature', 'text')


def run(doc_id, sent_id, words, lemmas, poses, ners, dep_paths, dep_parents, mention_id, wordidxs):
  try:
    import ddlib
  except:
    import os
    DD_HOME = os.environ['DEEPDIVE_HOME']
    from sys import path
    path.append('%s/ddlib' % DD_HOME)
    import ddlib

  def unpack_(begin_char_offsets, end_char_offsets, words, lemmas, poses, ners, dep_parents, dep_paths):
    wordobjs = []
    for i in range(0, len(words)):
      wordobjs.append(ddlib.Word(
          begin_char_offset=None,
          end_char_offset=None,
          word=words[i],
          lemma=lemmas[i],
          pos=poses[i],
          ner='',  # NER is noisy on medical docs
          dep_par=dep_parents[i],
          dep_label=dep_paths[i]))
    return wordobjs

  begin_char_offsets = None
  end_char_offsets = None

  sentence = unpack_(begin_char_offsets, end_char_offsets, words, lemmas,
                     poses, ners, dep_parents, dep_paths)
  span = ddlib.Span(begin_word_id=wordidxs[0], length=len(wordidxs))

  for feature in ddlib.get_generic_features_mention(sentence, span):
    yield doc_id, mention_id, feature
