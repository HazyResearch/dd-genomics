

#Here we assume that the ddlog database is accessible by "deepdive sql" so correctly defined in db.url

cd ..
deepdive sql """DROP VIEW IF EXISTS gene_mentions_filtered_is_correct_inference CASCADE;
CREATE VIEW gene_mentions_filtered_is_correct_inference AS SELECT
g.*,
ginf.category as category, 
ginf.expectation as expectation
from gene_mentions_filtered g,
gene_mentions_filtered_inference_label_inference ginf
where ginf.mention_id = g.mention_id;"""

deepdive sql """DROP VIEW IF EXISTS genepheno_causation_is_correct_inference CASCADE;
CREATE VIEW genepheno_causation_is_correct_inference AS SELECT
g.*,
ginf.category as category, 
ginf.expectation as expectation
from genepheno_causation g,
genepheno_causation_inference_label_inference ginf
where ginf.relation_id = g.relation_id;"""

deepdive sql """DROP VIEW IF EXISTS genepheno_association_is_correct_inference CASCADE;
CREATE VIEW genepheno_association_is_correct_inference AS SELECT
g.*,
ginf.category as category, 
ginf.expectation as expectation
from genepheno_association g,
genepheno_association_inference_label_inference ginf
where ginf.relation_id = g.relation_id;"""

# deepdive sql """
# DELETE FROM gene_holdout_set 
# WHERE (doc_id, section_id, sent_id, gene_wordidxs) IN 
# (SELECT DISTINCT
#   s.doc_id, s.section_id, s.sent_id, s.gene_wordidxs
# FROM
#   gene_holdout_set s 
#   LEFT JOIN 
#   gene_mentions_filtered p
#     ON (s.doc_id = p.doc_id AND s.section_id = p.section_id AND s.sent_id = p.sent_id AND s.gene_wordidxs = STRING_TO_ARRAY(p.wordidxs, '|~|')::INTEGER[]) WHERE p.doc_id IS NULL);
# 
# DELETE FROM gene_holdout_labels WHERE (doc_id, section_id, sent_id) NOT IN (SELECT DISTINCT doc_id, section_id, sent_id FROM gene_holdout_set);
# """
