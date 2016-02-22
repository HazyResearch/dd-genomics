copy (
select 
  g.doc_id
  , g.section_id
  , g.sent_id
  , g.wordidxs as wordidxs
  , string_to_array(si.words, '|^|') as words
  , g.mention_id
from
  split_words_mentions_filtered g
  join sentences_input si
    on (g.doc_id = si.doc_id
        and g.section_id = si.section_id
        and g.sent_id = si.sent_id)
group by
  g.doc_id
  , g.section_id
  , g.sent_id
  , g.wordidxs
  , si.words
  , g.mention_id
ORDER BY random()
LIMIT 1000
)
to stdout with csv header;
