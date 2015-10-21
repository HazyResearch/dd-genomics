copy (
select 
  hs.doc_id
  , hs.section_id
  , hs.sent_id
  , array_agg(DISTINCT genes.ensembl_id) as gene_id
  , g.wordidxs as gene_wordidxs
  , string_to_array(si.words, '|^|') as words
from
  (select distinct * from gene_holdout_set) hs
  join gene_mentions g
    on (hs.doc_id = g.doc_id
        and hs.section_id = g.section_id
        and hs.sent_id = g.sent_id
        and hs.gene_wordidxs = g.wordidxs)
  join sentences_input_with_gene_mention si
    on (hs.doc_id = si.doc_id
        and hs.section_id = si.section_id
        and hs.sent_id = si.sent_id)
  join genes
    on (g.gene_name = genes.gene_name)
where
  g.gene_name is not null
group by
  hs.doc_id
  , hs.section_id
  , hs.sent_id
  , g.wordidxs
  , si.words
)
to stdout with csv header;
