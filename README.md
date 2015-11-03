Porting to ddlog:

limitations:
    - a call to an elt of a tab doesn't work. Therefore, in the extractor "non_gene_acronyms_extract_candidates", the sql query is slightly different (doesn't include gm.wordidxs[1] and a.words[a.wordidx] LIKE '-LRB-';) and the udf is slightly changed in non_gene_acronyms_extract_candidates_ddlog.py to make this comparison in the python script.

    - bug in dependency for ddlog when a "not exists" is called. Therefore the pipeline is cut and deepdive called for the different pipelines so the dependency issue is solved that way (temporary since the ddlog compiler is fixed.)

    - "delete from" doesn't exist in ddlog, therefore, for gene_mentions, we have to create a temporary table gene_mentions_temp_before_non_gene_acronyms_delete_candidates which contains all the rows. Only the rows with the good criteria for non_gene_acronyms are put in gene_mentions.

    - In ddlog, we cannot add twice in pheno_mentions when the second addition requires the first one beforehand. Therefore, the table pheno_mentions_without_acronyms is first created, which is used to compute pheno_acronyms_aggregate_candidates. Then, the result of pheno_acronyms_insert_candidates and the initial extractions in pheno_mentions_without_acronyms are put in pheno_mentions

    - The shell script ${APP_HOME}/util/serialize_genepheno_pairs_split.sh genomics cannot be called during the deepdive run. Therefore we cut once again the pipeline to call this script.

    - The holdout fraction cannot be defined in ddlog. Therefore we add the sentence "calibration.holdout_fraction: 0.1" in the deepdive.conf file (while writing the pipelines. This writing is done in hack_pipelines.py)

    - in ddlog, when we create variables and inference rules, the variable is not just a column of an existing table, it has to be a new table. For instance, the variable is_true of gene_mentions_filtered, we create the table gene_mentions_filtered_inference. Therefore, don't forget to add in the pipeline the extractor linking the table_inference and the corresponding mention table !
    For instance, here, we have to add the extractor ext_gene_mentions_filtered_inference, otherwise the inference part doesn't bring any result...