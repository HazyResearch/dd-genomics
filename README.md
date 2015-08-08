# The Genomics DeepDive (GDD) Project

#### TO-DO LIST
See Milestones/Issues.

### DATA:
[8/8/15]: Current datasets to use:
* **PMC (includes PLoS):**
	* Raw XML documents: `/dfs/scratch0/ajratner/pmc_raw/`
	* Parsed into sections: `/dfs/scratch0/ajratner/parsed/pmc/xml/{pmc.json, pmc.md.tsv}`
	* Processed through coreNLP: `/dfs/scratch0/ajratner/parsed/pmc/corenlp/pmc.tsv`
	* In database: `genomics_production.sentences`
* **PubMed Titles + Abstracts:**
	* Raw XML documents: `/dfs/scratch0/jbirgmei/pubmed_baseline/ungz/`
	* Parsed into sections: `/dfs/scratch0/ajratner/parsed/pubmed_abs/xml/{pubmed_abs.json, pubmed_abs.md.tsv}`
	* Processed through coreNLP: `/dfs/scratch0/ajratner/parsed/pubmed_abs/corenlp/pubmed_abs.tsv`
	* In database: `genomics_production.sentences`

### Running GDD: Basics

1. For data pre-processing instructions, see [parser](parser)

2. Copy template file `env.sh` to `env_local.sh` and modify this file (it's ignored by git, and prefered by the run script).  Make sure to set:
	* database variables: user, host, port, db-name, db-type (postgres vs. greenplum)
	* _memory and parallelism options_
	* _relevant library paths_
	* _[GREENPLUM ONLY] port for gpfdist_

3. Create the database to be used if necessary (`createdb -U $DBUSER -h $DBHOST -p $DBPORT $DBNAME`)

4. [IF NO INPUT DATA LOADED] Create input schema by running: `./util/create_input_schema.sh` (**NOTE: this will drop any input data already loaded into `sentences` or `sentences_input` tables!**).  Then load data: if from tsv file you can use (usually loading `sentences_input` -> `TABLE_NAME=sentences_input`):

		./util/copy_table_from_file.sh [DB_NAME] [TABLE_NAME] [TSV_FILE_PATH]

  NOTE: To dump a table from psql to `.tsv` format for transfer in such a way, use: `COPY (SELECT * FROM [table_name]) TO '/tmp/[table_name].tsv' WITH DELIMITER '\t'`.

5. To refresh / create the schema, run `./util/create_schema.sh`- *note that this will drop any output data from previous runs*.

6. Make sure that the custom user functions have been loaded into Postgres for this user; to do so run `./util/add_user_functions.sh`.

7. Fetch and process ontology files: `cd onto; ./make_all.sh`

8. install nltk: `sudo pip install nltk`. Download the corpora wordnet: in Python: `import nltk; nltk.download()` and download the corpora wordnet.

9. Run the appropriate pipeline: `./run.sh [PIPELINE_NAME]`

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
