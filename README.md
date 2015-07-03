# The Genomics DeepDive (GDD) Project

### TO-DO LIST [updated 7/3/15]

#### High-level / major
* Get Dashboard up & running with Charite comparison script included [work with Jaeho & Mike]
* GP: Handle / better define causal vs. associative connection (use multinomial?)
* GP: Handle negation, also hypotheticals (e.g. "might be", "we hypothesize", etc.) *[See some initial attempts]
* G: Handle non-canonicals better, calibrate / increase precision 
* P: Integrate UMLS to increase vocabulary & better control synonyms list
* Add in genetic variant tagging (as preprocessing extractor)

#### Specific / minor
* [7/3/15] GP: too many negative supervisions with new rules for e.g. getting rid of "associated" / "correlated" & some negations / "might"! -> need to calibrate / adjust
* G: add supervision using acronym definition sections

### GDD Setup notes

1. [7/3/15]: The current testing / dev dataset is in the genomics_ajratner db (login as `psql -U ajratner -h raiders2 -p 6432 genomics_ajratner` -> then copy to own db) sentences table- this is 30k docs of PLoS XML-preprocessed evenly balanced between PLoS ONE & PLoS other.
2. [7/3/15]: The full PLoS + PMC XML data is currently being (slowly) copied to `/dfs/scratch0/ajratner/pmc_raw`.  A subset (PLoS) is already in `/dfs/scratch0/ajratner/dd_raw_docs`).
3. [5/28/15]: The sampler used is currently in the `sample_evidence` branch of the sampler [repo][sampler-se].  To use an existing compiled binary for linux, just move `util/sampler-dw-linux` to `$DEEPDIVE_HOME/util/sampler-dw-linux`.  To recompile the binary, clone the sampler repo, follow instructions, then move the compiled binary to the same location.

### Running GDD: Basics

*NOTE [Mac OSX]: If running on Mac OSX, some of the scripts used below (those using the linux `readlink` command) may fail; recommended fix for now is to hardcode paths locally...*

1. Copy template file `env.sh` to `env_local.sh` and modify this file (it's ignored by git, and prefered by the run script).  Make sure to set:
	* database variables: user, host, port, db-name, db-type (postgres vs. greenplum)
	* _memory and parallelism options_
	* _relevant library paths_
	* _[GREENPLUM ONLY] port for gpfdist_

2. Create the database to be used if necessary

3. [IF NO INPUT DATA LOADED] **If no existing input data (e.g. `sentences` and/or `sentences_input` tables) is loaded:** Create input schema by running `./util/create_input_schema.sh` (**NOTE: this will drop any input data already loaded!**).  Then load data: if from tsv file you can use (usually loading `sentences_input` -> `TABLE_NAME=sentences_input`):

		./util/copy_table_from_file.sh [DB_NAME] [TABLE_NAME] [TSV_FILE_PATH]

  NOTE: some ready-to-use data files are available on `raiders2` at `/lfs/raiders2/0/robinjia/data/genomics_sentences_input_data/`.
`genomics_10k_sentences.tsv` has 10k sentences (good for quick testing and debugging) and `genomics_50k_docs.tsv` has 50k documents 
(gene extraction takes about 2 hours on `raiders2`).
There is also `plos_all_docs.tsv`, a separate, cleaner dataset based on HTML dumps from PLoS.
If you want to run certain mindtagger tasks (namely pheno-recall),
you will also need to copy 
`/lfs/raiders2/0/robinjia/data/genomics_sentences_input_data/hpo_to_plos_doc_id.tsv`
to the `hpo_to_doc_via_mesh` table.

4. To refresh / create the schema, run `./util/create_schema.sh`- *note that this will drop any output data from previous runs*.

5. Make sure that the custom user functions have been loaded into Postgres for this user; to do so run `./util/add_user_functions.sh`.

6. [GREENPLUM ONLY] Make sure that GreenPlum's parallel file distribution server, `gpfdist`, is running with the correct settings (e.g. run `ps aux | grep gpfdist`; make sure that an intance is running with the correct $GPPATH and $GPPORT).  If not, then start a new one running on a free port:

		gpfdist -d ${GPPATH} -p ${GPPORT} -m 268435456 &

7. Fetch and process ontology files: `cd onto; ./make_all.sh`

8. Run the appropriate pipeline: `./run.sh [PIPELINE_NAME]`

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
