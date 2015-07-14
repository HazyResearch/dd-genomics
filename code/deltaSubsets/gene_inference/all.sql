create table gene_old_inferences_of_interest as
  (select
    r.*
   from
    gene_mentions_is_correct_inference_snapshot r join
    sentences_input si on (r.sent_id = si.sent_id and r.doc_id = si.doc_id));
create table gene_new_inferences_of_interest as
  (select
    r.*
   from
    gene_mentions_is_correct_inference r join
    sentences_input si on (r.sent_id = si.sent_id and r.doc_id = si.doc_id));
