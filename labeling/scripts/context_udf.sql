CREATE TABLE preceding_sentences as
	select doc_id, sent_id, array_accum(words) as sents from
	( select t0.doc_id as doc_id, t0.sent_id as sent_id, t1.sent_id as sent_id_2, array_to_string(t1.words, ' ') as words from sentences t0, sentences t1
	where t0.doc_id = t1.doc_id and t1.sent_id >= t0.sent_id - 2 and t1.sent_id < t0.sent_id order by t0.doc_id, t0.sent_id, t1.sent_id ) tmp
	group by doc_id, sent_id
DISTRIBUTED BY (doc_id);

CREATE TABLE following_sentences as
	select doc_id, sent_id, array_accum(words) as sents from
	( select t0.doc_id as doc_id, t0.sent_id as sent_id, t1.sent_id as sent_id_2, array_to_string(t1.words, ' ') as words from sentences t0, sentences t1
	where t0.doc_id = t1.doc_id and t1.sent_id <= t0.sent_id + 2 and t1.sent_id > t0.sent_id order by t0.doc_id, t0.sent_id, t1.sent_id ) tmp
	group by doc_id, sent_id
DISTRIBUTED BY (doc_id);
