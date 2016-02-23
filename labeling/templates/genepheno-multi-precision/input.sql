copy (
select DISTINCT
  hs.doc_id
  , hs.section_id
  , hs.sent_id
  , array_agg(DISTINCT genes.ensembl_id) as gene_id
  , p.entity as pheno_id
  , g.wordidxs as gene_wordidxs
  , p.wordidxs as pheno_wordidxs
  , string_to_array(si.words, '|^|') as words
  , ARRAY_TO_STRING(STRING_TO_ARRAY(lower(ap.names), '|^|'), ', ') as pheno_name
  , g.mention_id
  , p.mention_id
from
  (SELECT
      gp.doc_id,
      gp.section_id,
      gp.sent_id,
      string_to_array(gp.gene_wordidxs, '|^|')::int[] AS gene_wordidxs,
      string_to_array(gp.pheno_wordidxs, '|^|')::int[] AS pheno_wordidxs,
      gp.gene_mention_id AS gene_mention_id,
      gp.pheno_mention_id AS pheno_mention_id,
      gp.gene_mention_id || '_' || gp.pheno_mention_id AS relation_id
    FROM
      genepheno_pairs gp
      join genes g
        on (gp.gene_name = g.gene_name)
      join (select g.doc_id, g.section_id, g.sent_id, count(g.mention_id) num_gene_candidates
            from gene_mentions_filtered g
              join gene_mentions_filtered_inference_label_inference i
                on (g.mention_id = i.mention_id)
            WHERE i.expectation > 0.5
            group by g.doc_id, g.section_id, g.sent_id) ng
        on (gp.doc_id = ng.doc_id and gp.section_id = ng.section_id and gp.sent_id = ng.sent_id)
      join num_pheno_candidates np
        on (gp.doc_id = np.doc_id and gp.section_id = np.section_id and gp.sent_id = np.sent_id)
    WHERE
      ng.num_gene_candidates >= 3
      AND np.num_pheno_candidates >= 3
  ) hs
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
  join genepheno_causation_inference_label_inference gpi
    on (hs.relation_id = gpi.relation_id)
  join pheno_names ap 
    on (ap.id = p.entity)
where
  gpi.expectation > 0.75
group by
  hs.doc_id
  , hs.section_id
  , hs.sent_id
  , p.entity
  , g.wordidxs
  , p.wordidxs
  , si.words
  , ap.names
  , g.mention_id
  , p.mention_id
order by random()
LIMIT 1000
)
to stdout with csv header;
