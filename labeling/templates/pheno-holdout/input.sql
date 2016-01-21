copy (
select 
  hs.doc_id
  , hs.section_id
  , hs.sent_id
  , p.entity as pheno_name
  , p.wordidxs as pheno_wordidxs
  , string_to_array(si.words, '|^|') as words
  , p.mention_id
from
  (select distinct * from pheno_holdout_set) hs
  join pheno_mentions p
    on (hs.mention_id = p.mention_id)
  join sentences_input si
    on (hs.doc_id = si.doc_id
        and hs.section_id = si.section_id
        and hs.sent_id = si.sent_id)
where
  p.entity is not null
group by
  hs.doc_id
  , hs.section_id
  , hs.sent_id
  , p.entity
  , p.wordidxs
  , si.words
  , p.mention_id
)
to stdout with csv header;
