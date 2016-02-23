-- Basic stats post-run *for GP*

-- Number of features
SELECT COUNT(*) AS "Number of features" FROM genepheno_features;

-- Top features
-- Need to do `deepdive do weights` first!
SELECT description, weight FROM dd_inference_result_variables_mapped_weights WHERE description LIKE 'inf_istrue_genepheno_causation%' ORDER BY weight DESC LIMIT 50;

-- Supervised label distribution
SELECT is_correct, COUNT(*) FROM genepheno_causation GROUP BY is_correct;
SELECT supertype, is_correct, COUNT(*) FROM genepheno_causation GROUP BY supertype, is_correct;

-- Binned expectations
SELECT
  CASE
    WHEN expectation BETWEEN 0 and 0.1 THEN '0'
    WHEN expectation BETWEEN 0.1 and 0.2 THEN '0.1'
    WHEN expectation BETWEEN 0.2 and 0.3 THEN '0.2'
    WHEN expectation BETWEEN 0.3 and 0.4 THEN '0.3'
    WHEN expectation BETWEEN 0.4 and 0.5 THEN '0.4'
    WHEN expectation BETWEEN 0.5 and 0.6 THEN '0.5'
    WHEN expectation BETWEEN 0.6 and 0.7 THEN '0.6'
    WHEN expectation BETWEEN 0.7 and 0.8 THEN '0.7'
    WHEN expectation BETWEEN 0.8 and 0.9 THEN '0.8'
    WHEN expectation BETWEEN 0.9 and 1 THEN '0.9'
  END AS binned_exp,
  COUNT(*)
FROM genepheno_causation_inference_label_inference
GROUP BY binned_exp
ORDER BY binned_exp;
