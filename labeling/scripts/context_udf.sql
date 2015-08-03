CREATE TABLE preceding_sentences AS
  SELECT 
    doc_id, section_id, sent_id, array_accum(words) AS sents FROM
	(SELECT t0.doc_id AS doc_id, t0.section_id AS section_id, t0.sent_id AS sent_id, t1.sent_id AS sent_id_2, array_to_string(t1.words, ' ') AS words FROM sentences t0, sentences t1
	 WHERE t0.doc_id = t1.doc_id AND t0.section_id = t1.section_id AND t1.sent_id >= t0.sent_id - 2 AND t1.sent_id < t0.sent_id ORDER BY t0.doc_id, t0.section_id, t0.sent_id, t1.sent_id) tmp
	GROUP BY doc_id, section_id, sent_id
DISTRIBUTED BY (doc_id, section_id);

CREATE TABLE following_sentences AS
	SELECT doc_id, section_id, sent_id, array_accum(words) AS sents FROM
	(SELECT t0.doc_id AS doc_id, t0.section_id AS section_id, t0.sent_id AS sent_id, t1.sent_id AS sent_id_2, array_to_string(t1.words, ' ') AS words FROM sentences t0, sentences t1
	 WHERE t0.doc_id = t1.doc_id AND t0.section_id = t1.section_id AND t1.sent_id <= t0.sent_id + 2 AND t1.sent_id > t0.sent_id ORDER BY t0.doc_id, t0.section_id, t0.sent_id, t1.sent_id) tmp
	GROUP BY doc_id, section_id, sent_id
DISTRIBUTED BY (doc_id, section_id);
