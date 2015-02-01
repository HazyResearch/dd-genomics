COPY (
  SELECT 
    doc_id, sent_id, words
  FROM 
    sentences
  WHERE
    doc_id IN (
      SELECT 
        doc_id
      FROM 
        doc_source
      WHERE
        source = 'pmed'
      ORDER BY random()
      LIMIT 10
    )
) TO STDOUT WITH CSV HEADER;
