Setting the dd-genomics repo: 

- define a db.url file, such as postgresql://localhost:6432/genomics_tpalo (the number being the port and the noun is the name of the database you want to create).
 
- Pre-process & load the data: See the Parser README (https://github.com/HazyResearch/dd-genomics/tree/master/parser) for detailed instructions
- Make sure that the custom user functions have been loaded into Postgres for this user; to do so run ./util/add_user_functions.sh.

- Fetch and process ontology files: cd onto; ./make_all.sh

 - Install nltk: sudo pip install nltk. Download the corpora wordnet: in Python: import nltk; nltk.download() and download the corpora wordnet.
 

- compile the application with the command "deepdive compile"














Switching to ddlog:

Main changes from application.conf:

	- many temporary tables and views (due to complicated sql queries that cannot be translated directly in ddlog). This should not effect the speed of the process.

limitations and remarks:
    - inputs are now done with the same "deepdive do ..." command. Therefore, all the inputs and loads are put in the folder input/ which contains scripts or aliases to the real data (most of the time in onto/).

    - a call to an elt of a tab doesn't work. Therefore, in the extractor "non_gene_acronyms_extract_candidates", the sql query is slightly different (doesn't include gm.wordidxs[1] and a.words[a.wordidx] LIKE '-LRB-';) and the udf is slightly changed in non_gene_acronyms_extract_candidates_ddlog.py to make this comparison in the python script.


    - "delete from" doesn't exist in ddlog, therefore, for gene_mentions, we have to create a temporary table gene_mentions_temp_before_non_gene_acronyms_delete_candidates which contains all the rows. Only the rows with the good criteria for non_gene_acronyms are put in gene_mentions.

    - In ddlog, we cannot add twice in pheno_mentions when the second addition requires the first one beforehand. Therefore, the table pheno_mentions_without_acronyms is first created, which is used to compute pheno_acronyms_aggregate_candidates. Then, the result of pheno_acronyms_insert_candidates and the initial extractions in pheno_mentions_without_acronyms are put in pheno_mentions

    - The shell script ${APP_HOME}/util/serialize_genepheno_pairs_split.sh genomics cannot be translated in ddlog during the deepdive run. Therefore we add it in a deepdive.conf file with the corresponding input and output table and it is correctly placed in the whole run.

    - The holdout fraction cannot be defined in ddlog. Therefore we can add the sentence "calibration.holdout_fraction: 0.1" in the deepdive.conf file.

    - in ddlog, when we create variables and inference rules, the variable is not just a column of an existing table, it has to be a new table. For instance, the variable is_true of gene_mentions_filtered, we create the table gene_mentions_filtered_inference.
