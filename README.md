Porting to ddlog:

#### TO-DO LIST
See Milestones/Issues.

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

### Running GDD: Basics

1. Copy template file `env.sh` to `env_local.sh` and modify this file (it's ignored by git, and prefered by the run script).  Make sure to set:
	* database variables: user, host, port, db-name, db-type (postgres vs. greenplum)
	* _memory and parallelism options_
	* _relevant library paths_
	* _[GREENPLUM ONLY] port for gpfdist_

2. Create the database to be used if necessary (`createdb -U $DBUSER -h $DBHOST -p $DBPORT $DBNAME`)

3. Create the *input* data schema by running: `./util/create_input_schema.sh` (**NOTE that this will drop any input data already loaded into e.g. `sentences` or `sentences_input` tables**)

4. To refresh / create the *extractor* schema, run `./util/create_schema.sh` (**NOTE that this will drop any output data from previous runs**).

5. **Pre-process & load the data: See the [Parser README](parser) for detailed instructions**

6. Make sure that the custom user functions have been loaded into Postgres for this user; to do so run `./util/add_user_functions.sh`.

7. Fetch and process ontology files: `cd onto; ./make_all.sh`

8. Install nltk: `sudo pip install nltk`. Download the corpora wordnet: in Python: `import nltk; nltk.download()` and download the corpora wordnet.

9. Run the appropriate pipeline: `./run.sh [PIPELINE_NAME]`.  **ATTENTION: NEEDS PYTHON 2.7 at least.** Current key pipelines to use:
	1. **`preprocess`:** Serialize the sentences, etc. (any other operations only dependent on the input data i.e. the `sentences` table should go here)
	2. **`full_pipeline_gp`:** Run the extractors for G, P, and G-P; this is the union of `extractors_gp` and `inference_gp`
	3. **`postprocess`:** Aggregate the entity-level relations for the API, etc. (any other operations dependent on extraction & inference should go here)

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

### Limitations

    - a call to an elt of a tab doesn't work. Therefore, in the extractor "non_gene_acronyms_extract_candidates", the sql query is slightly different (doesn't include gm.wordidxs[1] and a.words[a.wordidx] LIKE '-LRB-';) and the udf is slightly changed in non_gene_acronyms_extract_candidates_ddlog.py to make this comparison in the python script.

    - bug in dependency for ddlog when a "not exists" is called. Therefore the pipeline is cut and deepdive called for the different pipelines so the dependency issue is solved that way (temporary since the ddlog compiler is fixed.)

    - "delete from" doesn't exist in ddlog, therefore, for gene_mentions, we have to create a temporary table gene_mentions_temp_before_non_gene_acronyms_delete_candidates which contains all the rows. Only the rows with the good criteria for non_gene_acronyms are put in gene_mentions.

    - In ddlog, we cannot add twice in pheno_mentions when the second addition requires the first one beforehand. Therefore, the table pheno_mentions_without_acronyms is first created, which is used to compute pheno_acronyms_aggregate_candidates. Then, the result of pheno_acronyms_insert_candidates and the initial extractions in pheno_mentions_without_acronyms are put in pheno_mentions

    - THe shell script ${APP_HOME}/util/serialize_genepheno_pairs_split.sh genomics cannot be called during the deepdive run. Therefore we cut once again the pipeline to call this script.
