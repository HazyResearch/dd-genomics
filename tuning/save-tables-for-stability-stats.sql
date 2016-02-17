DROP TABLE IF EXISTS genepheno_causation_inference_label_inference_prev;
CREATE TABLE genepheno_causation_inference_label_inference_prev AS (
  SELECT * FROM genepheno_causation_inference_label_inference);

DROP TABLE IF EXISTS dd_inference_result_variables_mapped_weights_prev;
CREATE TABLE dd_inference_result_variables_mapped_weights_prev AS (
  SELECT * FROM dd_inference_result_variables_mapped_weights);
