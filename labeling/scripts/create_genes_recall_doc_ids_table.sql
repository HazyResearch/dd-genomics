CREATE TABLE genes_recall_doc_ids AS (
	SELECT DISTINCT doc_id, section_id
	FROM gene_mentions_is_correct_inference
	WHERE expectation > 0.95
	ORDER BY random()
	LIMIT 10)
DISTRIBUTED BY (doc_id, section_id);
