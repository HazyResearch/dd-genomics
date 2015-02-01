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
        hpoterm_mentions
      WHERE
        entity = 'HP:0000717|Autism'
      ORDER BY random()
      LIMIT 10
    )
) TO STDOUT WITH CSV HEADER;
