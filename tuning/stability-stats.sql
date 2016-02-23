-- Get the average absolute difference between marginals from this run and preceding one
SELECT
  avg(abs(i0.expectation - i1.expectation)) AS "Mean Abs. Diff.- Marginals"
FROM
  genepheno_causation_inference_label_inference_prev i0,
  genepheno_causation_inference_label_inference i1
WHERE
  i0.relation_id = i1.relation_id;

-- Get the average relative absolute difference between weights from this run and preceding one
SELECT
  AVG(
    CASE 
      WHEN w0.weight > 0 OR w1.weight > 0 THEN 2*abs(w0.weight - w1.weight) / (abs(w0.weight) + abs(w1.weight))
      ELSE 0
    END
  ) AS "Mean Rel. Abs. Diff.- Weights"
FROM
  dd_inference_result_variables_mapped_weights_prev w0,
  dd_inference_result_variables_mapped_weights w1
WHERE
  w0.description = w1.description;
