copy (
select 
  g.doc_id
  , g.section_id
  , g.sent_id
  , array_agg(DISTINCT genes.ensembl_id) as gene_id
  , g.wordidxs as gene_wordidxs
  , string_to_array(si.words, '|^|') as words
  , g.mention_id
from
  gene_mentions_filtered g
  join sentences_input si
    on (g.doc_id = si.doc_id
        and g.section_id = si.section_id
        and g.sent_id = si.sent_id)
  join genes
    on (g.gene_name = genes.gene_name)
where
  g.gene_name is not null
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
