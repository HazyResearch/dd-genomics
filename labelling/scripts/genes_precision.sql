COPY (
SELECT 
	t0.mention_id,
	t0.entity,
	t0.wordidxs, 
	t1.words,
	t2.array_accum as prec,
	t3.array_accum as foll
FROM
	gene_mentions_is_correct_inference t0, 
	sentences t1,
	preceding_sentences t2,
	following_sentences t3
WHERE
	t0.doc_id = t1.doc_id AND t0.sent_id = t1.sent_id
AND 
	t0.doc_id = t2.doc_id AND t0.sent_id = t2.sent_id
AND 
	t0.doc_id = t3.doc_id AND t0.sent_id = t3.sent_id
AND 
	t0.expectation > 0.9
ORDER BY random()
LIMIT 200
) TO STDOUT
;

