SELECT t0.genes_mentions_feature, t1.cardinality, t1.weight FROM dd_weights_genes_mentions_is_correct t0, dd_inference_result_variables_mapped_weights t1 WHERE t1.id = t0.id ORDER BY t1.weight;
