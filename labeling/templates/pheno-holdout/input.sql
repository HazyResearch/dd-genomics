copy (
select 
  p.doc_id
  , p.section_id
  , p.sent_id
  , p.entity as pheno_id
  , string_to_array(p.wordidxs, '|^|')::int[] as pheno_wordidxs
  , string_to_array(si.words, '|^|') as words
  , ap.names as pheno_name
  , p.mention_id
from
  pheno_mentions_filtered p
  join sentences_input si
    on (p.doc_id = si.doc_id
        and p.section_id = si.section_id
        and p.sent_id = si.sent_id)
  join pheno_names ap
    on (ap.id = p.entity)
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
  , ap.names
ORDER BY random()
LIMIT 1000
)
to stdout with csv header;
