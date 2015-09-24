copy (
select DISTINCT ON (si.words)
  si.doc_id
  , si.section_id
  , si.sent_id
  , g.gene_name as gene_name
  , p.entity as pheno_name
  , g.wordidxs as gene_wordidxs
  , p.wordidxs as pheno_wordidxs
  , string_to_array(si.words, '|^|') as words
from
  sentences_input si
  join genepheno_pairs gp
    on (si.doc_id = gp.doc_id
        and si.section_id = gp.section_id
        and si.sent_id = gp.sent_id)
  join gene_mentions g
    on (si.doc_id = g.doc_id
        and si.section_id = g.section_id
        and si.sent_id = g.sent_id) 
  join pheno_mentions p
    on (si.doc_id = p.doc_id
        and si.section_id = p.section_id
        and si.sent_id = p.sent_id)
where
  (si.doc_id = '22442688' or si.doc_id = '25167861' or si.doc_id = '25531106' or si.doc_id = '20705735' or si.doc_id = '25531106' or si.doc_id = '25531106' or si.doc_id = '22442688' or si.doc_id = '25167861') AND
  g.gene_name = 'DEAF1'
  AND (p.is_correct = 't' OR p.is_correct is null)
)
to stdout with csv header;
