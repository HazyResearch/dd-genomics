copy (
select 
  hs.doc_id
  , hs.section_id
  , hs.sent_id
  , array_agg(genes.ensembl_id) as gene_id
  , p.entity as pheno_name
  , g.wordidxs as gene_wordidxs
  , p.wordidxs as pheno_wordidxs
  , string_to_array(si.words, '|^|') as words
from
  (select distinct * from genepheno_holdout_set) hs
  join gene_mentions g
    on (hs.doc_id = g.doc_id
        and hs.section_id = g.section_id
        and hs.sent_id = g.sent_id
        and hs.gene_wordidxs = g.wordidxs)
  join pheno_mentions p
    on (hs.doc_id = p.doc_id
        and hs.section_id = p.section_id
        and hs.sent_id = p.sent_id
        and hs.pheno_wordidxs = p.wordidxs)
  join sentences_input si
    on (hs.doc_id = si.doc_id
        and hs.section_id = si.section_id
        and hs.sent_id = si.sent_id)
  join genes
    on (g.gene_name = genes.gene_name)
  group by
    hs.doc_id
    , hs.section_id
    , hs.sent_id
    , p.entity
    , g.wordidxs
    , p.wordidxs
    , si.words
)
to stdout with csv header;
