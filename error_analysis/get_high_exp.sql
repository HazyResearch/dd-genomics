SELECT 
	t0.doc_id,
	t0.sent_id, 
	t0.words, 
	t0.expectation,
	t0.is_correct,
	t0.features,
	t1.words
FROM
	gene_mentions_is_correct_inference t0, 
	sentences t1 
WHERE
	t0.doc_id = t1.doc_id AND t0.sent_id = t1.sent_id
AND 
	t0.expectation > 0.9
;

