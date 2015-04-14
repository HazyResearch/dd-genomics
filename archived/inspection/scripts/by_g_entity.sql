COPY (
  SELECT 
    doc_id, sent_id, words
  FROM 
    sentences
  WHERE
    doc_id IN (
      SELECT 
        DISTINCT(doc_id)
      FROM 
        gene_mentions
      WHERE
        entity = 'CDH17'
      ORDER BY random()
      LIMIT 10
    )
) TO STDOUT WITH CSV HEADER;
