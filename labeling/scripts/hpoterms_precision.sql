COPY (
SELECT  t0.mention_id  as mention_id
     ,  t0.entity      as entity_name
     ,  t0.wordidxs    as mention_pos
     ,  t1.words       as words
     ,  t2.array_accum as sentences_before
     ,  t3.array_accum as sentences_after
FROM
	hpoterm_mentions_is_correct_inference t0, 
	sentences t1,
	preceding_sentences t2,
	following_sentences t3
WHERE
	t0.doc_id = t1.doc_id AND t0.section_id = t1.section_id AND t0.sent_id = t1.sent_id
AND 
	t0.doc_id = t2.doc_id AND t0.section_id = t2.section_id AND t0.sent_id = t2.sent_id
AND 
	t0.doc_id = t3.doc_id AND t0.section_id = t3.section_id AND t0.sent_id = t3.sent_id
AND 
	t0.expectation > 0.9
ORDER BY random()
LIMIT 100
) TO STDOUT WITH HEADER
;
