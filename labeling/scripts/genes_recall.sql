COPY (
WITH tmp AS (
        SELECT t0.doc_id AS doc_id
               , t0.section_id AS section_id
               , t0.sent_id AS sent_id
               , t0.words AS words
        FROM 
                sentences t0,
                genes_recall_doc_ids t1
        WHERE t0.doc_id = t1.doc_id AND t0.section_id = t1.section_id), 
         tmp1 AS (
        SELECT t0.doc_id
               , t0.section_id
               , t0.sent_id
               , t0.wordidxs
        FROM 
                gene_mentions_is_correct_inference t0,
                genes_recall_doc_ids t1
        WHERE t0.doc_id = t1.doc_id AND t0.section_id = t1.section_id
        AND t0.expectation > 0.9) 
SELECT t0.doc_id AS doc_id
       , t0.section_id AS section_id
       , t0.sent_id AS sent_id
       , t0.words AS words
       , array_accum(array_to_string(t1.wordidxs, '|')) AS positions
FROM
        tmp t0
LEFT JOIN 
        tmp1 t1
ON
        t0.doc_id = t1.doc_id AND t0.section_id = t1.section_id AND t0.sent_id = t1.sent_id
GROUP BY t0.doc_id, t0.section_id, t0.sent_id, t0.words
ORDER BY t0.doc_id, t0.section_id, t0.sent_id
) TO STDOUT WITH HEADER;
