create table genepheno_old_inferences_of_interest as
  (select
    r.*
   from
    genepheno_relations_is_correct_inference_snapshot r join
    sentences_input si on (r.sent_id = si.sent_id and r.doc_id = si.doc_id)
   where si.words like '%|^|might^|%');
create table genepheno_new_inferences_of_interest as
  (select
    r.*
   from
    genepheno_relations_is_correct_inference r join
    sentences_input si on (r.sent_id = si.sent_id and r.doc_id = si.doc_id)
   where si.words like '%|^|might|^|%');
