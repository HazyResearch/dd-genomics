copy (
select 
  p.doc_id
  , p.section_id
  , p.sent_id
  , p.entity as pheno_name
  , p.wordidxs as pheno_wordidxs
  , string_to_array(si.words, '|^|') as words
  , p.mention_id
from
  pheno_mentions p
  join sentences_input si
    on (p.doc_id = si.doc_id
        and p.section_id = si.section_id
        and p.sent_id = si.sent_id)
where
  p.entity is not null
group by
  p.doc_id
  , p.section_id
  , p.sent_id
  , p.entity
  , p.wordidxs
  , si.words
  , p.mention_id
ORDER BY random()
LIMIT 1000
)
to stdout with csv header;
