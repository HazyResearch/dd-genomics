copy (
select 
  hs.doc_id
  , hs.section_id
  , hs.sent_id
  , g.gene_entity as gene_name
  , p.pheno_entity as pheno_name
  , hs.gene_wordidxs as gene_wordidxs
  , hs.pheno_wordidxs as pheno_wordidxs
  , string_to_array(si.words, '|^|') as words
from
  holdout_set hs
  join gene_mentions g
    on (hs.doc_id = g.doc_id
        and hs.section_id = g.section_id
        and hs.sent_id = g.sent_id
        and string_to_array(hs.gene_wordidxs, '|~|')::integer[] = g.wordidxs)
  join pheno_mentions p
    on (hs.doc_id = p.doc_id
        and hs.section_id = p.section_id
        and hs.sent_id = p.sent_id
        and string_to_array(hs.pheno_wordidxs, '|~|')::integer[] = p.wordidxs)
  join sentences_input si
    on (hs.doc_id = si.doc_id
        and hs.section_id = si.section_id
        and hs.sent_id = si.sent_id)
)
to stdout with csv header;
