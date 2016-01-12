Setting the dd-genomics repo: 

- define a db.url file, such as greenplum://localhost:6432/genomics_tpalo (the number being the port and the noun is the name of the database you want to create), or more likely something like postgresql://localhost/genomics_tpalo if you're doint it locally.
 
- Pre-process & load the data: See the Parser README (https://github.com/HazyResearch/dd-genomics/tree/master/parser) for detailed instructions
- Make sure that the custom user functions have been loaded into Postgres for this user; to do so run ./util/add_user_functions.sh.

- Fetch and process ontology files: cd onto; ./make_all.sh

 - Install nltk: sudo pip install nltk. Download the corpora wordnet: in Python: import nltk; nltk.download() and download the corpora wordnet.

 - Define a input/sentences_input.* for which the sentences_input will be loaded, either an alias of the dataset. 
 
- compile the application with the command "deepdive compile"


Running the application: 


 - Run the command "deepdive do ..." with the name of the table you want to fill. Deepdive will suggest you all the operations it has to do for that. For instance, if you want to run the whole pipeline, run "deepdive do model/calibration-plots". 

  - If one of the inputs is a sql file, there will likely be an error with deepdive for too big sql files during a deepdive run, so just run the following (here for instance with sentences_input):
 		- deepdive sql < input/sentences_input.sql
 		- deepdive mark done sentences_input
 That will do the trick

 - To mark as done or todo some tables, use the command "deepdive mark ...". For instance, if you want each process to be mark as undone, run "deepdive mark todo init/db" 

 - Run "deepdive plan" to see all the operations possibles.

 - Overall, just run "deepdive" to see all the commands possible.
 
 - you can have access at the overall flow of the application in ${APP_HOME}/run/dataflow.svg (Chrome for instance works well for it).
 














Main changes from application.conf:

	- During a run, the driver now fills out a temporary table and replaces the corresponding table only at the end of the run of an extractor. Therefore, no more loss of data if a run is stopped in the middle. 

	- The column on which the table will be distributed by on greenplum is now defined by the annotation @distributed_by in front of the respective column. The driver will detect if the db used is postgres or greenplum (done by precising it in db.url) and add the "distributed by ..." statement only if needed, therefore no need to distringuish the app.ddlog file between psql and greenplum.

	- To create views, look at the documentation in /lfs/raiders7/0/tpalo/dd-genomics_for_views (to come soon).

	- For more information about the ddlog language, look at http://deepdive.stanford.edu/doc/basics/ddlog.html and https://github.com/HazyResearch/dd-genomics.

	- Slight bug in the compiler for now, when a view is defined by an extractor in app.ddlog, the command "deepdive compile" returns an error precising that the table is not declared. This can be fixed by adding: deepdive.schema.relations { name_of_th_view { "type": "view" } } in deepdive.conf.

	- many temporary tables and views (due to complicated sql queries that cannot be translated directly in ddlog). This should not effect the speed of the process.

    - inputs are now done with the same "deepdive do ..." command. Therefore, all the inputs and loads are put in the folder input/ which contains scripts or aliases to the real data (most of the time in onto/).

    - a call to an elt of a tab doesn't work. Therefore, in the extractor "non_gene_acronyms_extract_candidates", the sql query is slightly different (doesn't include gm.wordidxs[1] and a.words[a.wordidx] LIKE '-LRB-';) and the udf is slightly changed in non_gene_acronyms_extract_candidates_ddlog.py to make this comparison in the python script.


    - "delete from" doesn't exist in ddlog, therefore, for gene_mentions, we have to create a temporary table gene_mentions_temp_before_non_gene_acronyms_delete_candidates which contains all the rows. Only the rows with the good criteria for non_gene_acronyms are put in gene_mentions.

    - In ddlog, we cannot add twice in pheno_mentions when the second addition requires the first one beforehand. Therefore, the table pheno_mentions_without_acronyms is first created, which is used to compute pheno_acronyms_aggregate_candidates. Then, the result of pheno_acronyms_insert_candidates and the initial extractions in pheno_mentions_without_acronyms are put in pheno_mentions

    - The shell script ${APP_HOME}/util/serialize_genepheno_pairs_split.sh genomics cannot be translated in ddlog during the deepdive run. Therefore we add it in a deepdive.conf file with the corresponding input and output table and it is correctly placed in the whole run.

    - The holdout fraction cannot be defined in ddlog. Therefore we can add the sentence "calibration.holdout_fraction: 0.1" in the deepdive.conf file.

    - in ddlog, when we create variables and inference rules, the variable is not just a column of an existing table, it has to be a new table. For instance, the variable is_true of gene_mentions_filtered, we create the table gene_mentions_filtered_inference.
