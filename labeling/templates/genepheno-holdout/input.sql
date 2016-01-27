copy (
select 
  hs.doc_id
  , hs.section_id
  , hs.sent_id
  , array_agg(DISTINCT genes.ensembl_id) as gene_id
  , p.entity as pheno_name
  , g.wordidxs as gene_wordidxs
  , p.wordidxs as pheno_wordidxs
  , string_to_array(si.words, '|^|') as words
  , g.mention_id
  , p.mention_id
from
  (SELECT DISTINCT
      doc_id,
      section_id,
      sent_id,
      string_to_array(gene_wordidxs, '|~|')::int[] AS gene_wordidxs,
      string_to_array(pheno_wordidxs, '|~|')::int[] AS pheno_wordidxs,
      gp.gene_mention_id AS gene_mention_id,
      gp.pheno_mention_id AS pheno_mention_id
    FROM
      genepheno_pairs gp
    ORDER BY random()) hs
  join gene_mentions g
    on hs.gene_mention_id = g.mention_id
  join pheno_mentions p
    on hs.pheno_mention_id = p.mention_id
  join sentences_input si
    on (hs.doc_id = si.doc_id
        and hs.section_id = si.section_id
        and hs.sent_id = si.sent_id)
  join genes
    on (g.gene_name = genes.gene_name)
where
  g.gene_name is not null
  AND p.entity is not null
group by
  hs.doc_id
  , hs.section_id
  , hs.sent_id
  , p.entity
  , g.wordidxs
  , p.wordidxs
  , si.words
  , g.mention_id
  , p.mention_id
LIMIT 1000
)
to stdout with csv header;
