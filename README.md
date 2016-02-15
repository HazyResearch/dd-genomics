#### TO-DO LIST
See Milestones/Issues.


### SETUP:

Setting the dd-genomics repo:

1. Initialize \& update submodules: `git submodule update --init`.  (Note: you will need to have an SSH key for the computer being used set up with github, as well as have permission to access the submodule repos)

2. Define a `db.url` file, such as: `[postgres|greenplum]://localhost:6432/genomics_tpalo`

3. Copy template file `env.sh` to `env_local.sh` and modify this file with your local settings (it's ignored by git, and prefered by the run script).  Make sure to set your `PATH` so that the correct version of `psql` is on it. Be sure in particular to define the variable APP_HOME as the path to your dd-genomics repo. 

4.  Install nltk: `sudo pip install nltk`. Download the corpora wordnet: in Python: `import nltk; nltk.download()` and download the corpora wordnet.

5.  Fetch and process ontology files: `cd onto; ./make_all.sh`

6. Pre-process & load the data: See the [Parser README](https://github.com/HazyResearch/dd-genomics/tree/master/parser) for detailed instructions; then save the output table to `input/sentences_input.*` (or copy an existing sentences_input table to this location).

7. Source the environment vars: `source env_local.sh`.  **NOTE that this should be done before any deepdive run or action!**
 
8. Compile the application: `deepdive compile`


### Running DeepDive: 

* Run the command `deepdive do ...` with the name of the table you want to fill. Deepdive will suggest the operations it has to do related to this table, and select a plan including all upstream operations.  For example, if you want to run the whole pipeline, use `do` on the last table: `deepdive do calibration-plots`. 

* To mark as done (`done`), or conversely as yet to be done (`todo`), use the command `deepdive mark ...`. Deepdive will also mark all downstream operations.  For example, if you want each process to be mark as undone, use `do` on the first table: `deepdive mark todo init/db` 

* Run `deepdive plan` to see all the operations possibles.

* You can have access the overall flow of the application in `${APP_HOME}/run/dataflow.svg` (Chrome works well for this).

* Overall, just run `deepdive` to see all the commands possible.


### Running views

* You can prepare all the data by simply running script_views.sh 
Then run the commands displayed by :wq the different vim files (I will try to add a pipeline for that). After a certain time, the run should end after creating all the indexes required for the views.
You can then launch the views (very quick) by ES_HEAP_SIZE=25g; PORT=$RANDOM mindbender search gui. These intructions are displayed at the end of the script
The link to which access your views will be displayed in the terminal.

* A few comments:
	- is_charite_canon will be true if the element is in charite_canon and null if it is not. To easily access all the elements of a table not in charite canon, you can run the query in elastic search: _missing_: is_charite_canon
	- is_correct refers to the boolean defined during distant supervision rules. is_correct_labels refers to the boolean defined by the manual labels (and is null if the gene or gp is not labeled).
	- currently, the script exports all the tables in the database in postgres. This is certainly not optimized if the views have already been created once. Soon some specific scripts to update only part of the tables will come.
	- Only 6 features and weights are displayed currently in the views (the one with the most important absolute weights). If you want to display more features, you can click on {...} below the sentence and then on [...] in front of features and weights to display all of them. You can also modify the value of "limitTo" in mindbender/search-template/
	- Greenplum doesn't support the operations through which the views are created. Therefore, we here create another postgres database (done by modifying db.url) on port 15193, currently hosted on /lfs/raiders7/0/tpalo/pgdb_genomics. The scripts export many tables from greenplum to postgres by exporting them in the folder ../tables_for_views. This process could certainly be parallized and made faster. 
	- Once in views, you can search for instance for false negatives with the query: expectation: <0.9 is_correct:"T"


### Labeling data:
Go to `labeling/` and follow the documentation

### Evaluate the System

run `./evaluation.sh $RELATION $VERSION [$CONFIDENCE] [$OPTOUT]` where :
  - $RELATION can be either on of {gene,causation,association} 
  - $VERSION is a required arguments and refers to the holdout set version to use for evaluation
  - $CONFIDENCE is optional (default 0.9). It sets the confidence threshold at which the inference will be considered as true
  - $OPTOUT is optional and refers to the option of opting out of logging. If you don't want to log your current evaluation, simply write OPTOUT as a third argument. Note that you need to set the confidence if you want to do so.
  
The evaluation.sh script will compute the necessary statistics of your current performance using the holdout set and output the following files:
  - `stats-$RELATION.tsv`: contains the summary statistics plus a breakdown over the labelers
  - `TP.tsv`: contains the true positives with three columns (relation_id, label, labeler, expectation)
  - `FP.tsv`: contains the false positives with three columns (relation_id, label, labeler, expectation)
  - `FN.tsv`: contains the false negatives with three columns (relation_id, label, labeler, expectation)
  - `holdout_set.tsv`: contains the full holdout set along with the labels and labelers
  - `input_data`: contains a path to the input sentence data and the number of sentences for sanity check

These files are stored under `results_log/$USERNAME/$RELATION-$DATE/`.

**Note**: Only the stats files are shared via Github

**CAVEAT**: in the current implementation, changing the input data will require manual modification in the `compute_causation_stats.sh`, `compute_association_stats.sh`, `compute_gene_stats.sh` by updating the path of the sentences_input file.

### Error Analysis

The Error Analysis doc is at https://docs.google.com/document/d/1u6fPO55YGR5BpJOJTDypAt8MfQImhS9PF9E_bkCqiz8/edit?usp=sharing .

#### Raiders 7 notes...
* To use **mosh**:
```bash
mosh yourusername@raiders7
kinit
aklog
```


### DATA:
[8/8/15]: Current datasets to use (with *With `ROOT=/dfs/scratch0/ajratner`*):
* **Production set:**
	* **PMC (includes PLoS):**
		* Raw XML documents: `$ROOT/pmc_raw/`
		* Parsed into sections: `$ROOT/parsed/pmc/xml/{pmc.json, pmc.md.tsv}`
		* Processed through coreNLP: `$ROOT/parsed/pmc/corenlp/pmc.tsv`
	* **PubMed Titles + Abstracts:**
		* Raw XML documents: `/dfs/scratch0/jbirgmei/pubmed_baseline/ungz/`
		* Parsed into sections: `$ROOT/parsed/pubmed_abs/xml/{pubmed_abs.json, pubmed_abs.md.tsv}`
		* Processed through coreNLP: `$ROOT/parsed/pubmed_abs/corenlp/pubmed_abs.tsv`
	* **In database: `raiders2:genomics_production.{sentences, doc_metadata}`**

# OLD STUFF...

### Notes on Simple Debugging Routines

#### Basic TSV extractor debugging
In one very simple routine, we can just find some sentences in the databse that would be decent for testing; for example, for basic debugging of the `pheno_extract_candidates.py` UDF, we can execute the following query in psql:
	
	COPY (SELECT 
	        doc_id, sent_id, words, lemmas, poses, ners 
	      FROM sentences_input 
	      WHERE words LIKE '%myeloid%'
	      LIMIT 10)
	TO '/tmp/pheno_extractor_debugging_myeloid_10.tsv' 
	WITH DELIMITER '\t';

We then just debug using print statements in the code & etc. as we normally would with any standalone python script:

	python code/pheno_extract_candidates.py < /tmp/pheno_extractor_debugging_myeloid_10.tsv

### Running Dashboard for Reports

Make sure you have run `util/update-mindbender.sh` at least once.
It will download the `util/mindbender` command, which includes Mindtagger as well as Dashboard.

(On raiders2, to get the correct psql version, do: ```export
PATH=/dfs/scratch1/netj/wrapped/greenplum:$PATH``` first.)

 - Run the command "deepdive do ..." with the name of the table you want to fill. Deepdive will suggest you all the operations it has to do for that. For instance, if you want to run the whole pipeline, run "deepdive do model/calibration-plots". 

  - If one of the inputs is a sql file, there will likely be an error with deepdive for too big sql files during a deepdive run, so just run the following (here for instance with sentences_input):
 		- deepdive sql < input/sentences_input.sql
 		- deepdive mark done sentences_input
 That will do the trick

 - To mark as done or todo some tables, use the command "deepdive mark ...". For instance, if you want each process to be mark as undone, run "deepdive mark todo init/db" 

 - Run "deepdive plan" to see all the operations possibles.

 - Overall, just run "deepdive" to see all the commands possible.
 
 - you can have access at the overall flow of the application in ${APP_HOME}/run/dataflow.svg (Chrome for instance works well for it).
 
To produce a set of reports using Dashboard after a GDD run, use the following steps:
```bash
(
. env_local.sh
export GDD_PIPELINE=
util/mindbender snapshot
)
```
This will produce a set of reports under a directory pointed by `snapshot/LATEST` as configured in `snapshot-default.conf`.

To view the produced reports, you can use the Dashboard GUI by starting it with the following command and opening the URL it prints:
```bash
(
. env_local.sh
export GDD_PIPELINE=
PORT=12345 util/mindbender dashboard
)
```
You may need to change `PORT=12345` value if someone else is already using it.
When Dashboard URL is loaded in your web browser, you can navigate to the first snapshot in the top "View Snapshots" dropdown.


### Running Mindtagger for Labeling and Evaluation
Another great way to understand the output of the DeepDive system is to inspect a sample of indiviual examples and perform error analysis.
We use a GUI tool called [*Mindtagger*][mindtagger] to expedite the labeling tasks necessary for performing this evaluation.
Mindtagger provides a clean interface for inspecting individual mention candidates.

We have created a set of Mindtagger labeling templates for genomics-related tasks.  First, create a new task by running

	cd labeling
	./create-new-task.sh TASK

where TASK is the name of a labeling task (run `create-new-task.sh` with no arguments for a list of all tasks).
Currently, the most useful tasks are:

* gene-precision: Selects 100 random gene mention candidates with score > .9.  User should see if any of them are wrong gene mentions.
* gene-recall: Selects 100 random gene mention candidates with score < .9.  User should see if any of them are true gene mentions.
* pheno-precision.  Selects 100 random phenotype mention candidates with score > .9.  User should see if any of them are wrong phenotype mentions.
* pheno-recall.  ?
* genepheno-precision.  Selects 100 random genepheno candidates with score > .9.
* genepheno-recall.  Selects 100 random genepheno candidates with gene & pheno scores > .8 but genepheno relation score <= .9.

See `eval/` directory for specific scripts for evaluation in other ways (e.g. pheno recall evaluation against MeSH).

Once you've created your task(s), start the Mindtagger GUI by running:

	./start-gui.sh

and then open a browser to [localhost][localhost] to view all the created tasks & label data!

### Running the Dashboard Snapshot

To run a dashboard snapshot, do 

    (source ./env_local.sh; ./util/mindbender snapshot gill) 2>&1 | grep -v 'declare'

Then start the dashboard, if it's not already running, with

    (source env_local.sh
    export GDD_PIPELINE=
    PORT=XXXX util/mindbender dashboard
    )

[sampler-se]: https://github.com/HazyResearch/sampler/tree/sample_evidence
[deepdiverepo]: https://github.com/hazyresearch/deepdive
[deepdivedocs]: http://deepdive.stanford.edu/index.html#documentation
[mindtagger]: https://github.com/netj/mindbender
[braindump]: https://github.com/zifeishan/braindump
[postgres-pg-static]: https://github.com/postgres/postgres/blob/master/src/include/catalog/pg_statistic.h
[localhost]: http://localhost:8000
[docker-install]: https://docs.docker.com/installation/#installation
[dockerfile-1]: https://gist.github.com/adamwgoldberg/7075b2237f819483a067
[dd-extractors]: http://deepdive.stanford.edu/doc/basics/extractors.html

### PATH

Add the following to your zshrc on raiders7:

    export PATH=/lfs/raiders7/0/USERNAME/local/bin:/usr/local/greenplum-db/bin_wrapped:~/local/bin:/usr/local/jdk1.8.0_66/bin:/lfs/raiders7/0/USERNAME/deepdive/util:/lfs/raiders7/0/USERNAME/deepdive/util:$PATH

### Getting Data From NCBI

* ssh to one of the following IP addresses (the silk machines):
** 171.64.65.39 (this is silk04.stanford.edu)
** 171.64.65.43
** 171.64.65.44
** 171.64.65.70
** 171.64.65.72

* Type ftp ftp.ncbi.nlm.nih.gov
* Username: anonymous
* Password: bejerano@stanford.edu

* Go to the directory and start downloading
 

Main changes from application.conf:

	- During a run, the driver now fills out a temporary table and replaces the corresponding table only at the end of the run of an extractor. Therefore, no more loss of data if a run is stopped in the middle. 

	- The column on which the table will be distributed by on greenplum is now defined by the annotation @distributed_by in front of the respective column. The driver will detect if the db used is postgres or greenplum (done by precising it in db.url) and add the "distributed by ..." statement only if needed, therefore no need to distringuish the app.ddlog file between psql and greenplum.

	- To create views, look at the documentation in /lfs/raiders7/0/tpalo/dd-genomics_for_views (to come soon).

	- For more information about the ddlog language, look at http://deepdive.stanford.edu/doc/basics/ddlog.html and https://github.com/HazyResearch/dd-genomics.

	- Slight bug in the compiler for now, when a view is defined by an extractor in app.ddlog, the command "deepdive compile" returns an error precising that the table is not declared. This can be fixed by adding: deepdive.schema.relations { name_of_th_view { "type": "view" } } in deepdive.conf.

	- many temporary tables and views (due to complicated sql queries that cannot be translated directly in ddlog). This should not effect the speed of the process.

limitations and remarks:

    - inputs are now done with the same "deepdive do ..." command. Therefore, all the inputs and loads are put in the folder input/ which contains scripts or aliases to the real data (most of the time in onto/).

    - a call to an elt of a tab doesn't work. Therefore, in the extractor "non_gene_acronyms_extract_candidates", the sql query is slightly different (doesn't include gm.wordidxs[1] and a.words[a.wordidx] LIKE '-LRB-';) and the udf is slightly changed in non_gene_acronyms_extract_candidates_ddlog.py to make this comparison in the python script.


    - "delete from" doesn't exist in ddlog, therefore, for gene_mentions, we have to create a temporary table gene_mentions_temp_before_non_gene_acronyms_delete_candidates which contains all the rows. Only the rows with the good criteria for non_gene_acronyms are put in gene_mentions.

    - In ddlog, we cannot add twice in pheno_mentions when the second addition requires the first one beforehand. Therefore, the table pheno_mentions_without_acronyms is first created, which is used to compute pheno_acronyms_aggregate_candidates. Then, the result of pheno_acronyms_insert_candidates and the initial extractions in pheno_mentions_without_acronyms are put in pheno_mentions

    - The shell script ${APP_HOME}/util/serialize_genepheno_pairs_split.sh genomics cannot be translated in ddlog during the deepdive run. Therefore we add it in a deepdive.conf file with the corresponding input and output table and it is correctly placed in the whole run.

    - The holdout fraction cannot be defined in ddlog. Therefore we can add the sentence "calibration.holdout_fraction: 0.1" in the deepdive.conf file.

    - in ddlog, when we create variables and inference rules, the variable is not just a column of an existing table, it has to be a new table. For instance, the variable is_true of gene_mentions_filtered, we create the table gene_mentions_filtered_inference. Therefore, don't forget to add in the pipeline the extractor linking the table_inference and the corresponding mention table !
    For instance, here, we have to add the extractor ext_gene_mentions_filtered_inference, otherwise the inference part doesn't bring any result...
