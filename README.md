# The Genomics DeepDive (GDD) Project

We have a wiki for this project at
<http://dev.stanford.edu/confluence/display/collaborators/DeepDive+Genomics>

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


### Performing Labeling & Data Inspection Tasks
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

Hopefully, we'll eventually come up with a good way to assess phenotype extractor recall.

Once you've created your task(s), start the Mindtagger GUI by running:

	./start-gui.sh

and then open a browser to [localhost][localhost] to view all the created tasks & label data!



#### *Installing DeepDive via Docker*

1. Install Docker (see [Docker installation guide][docker-install])
2. Create a new directory with at least 20GB of free space, and copy the file named `Dockerfile` in this directory into it, then `cd` into it
3. Run the following:
		
		docker build -t deepdive . 
		docker run -d --privileged --name db -h gphost readr/greenplum
		docker run -t -d --link db:db --name deepdive deepdive bash
		docker exec -ti deepdive bash
		cd ~/deepdive
		make test

4. ***Note: currently we are having issues with running `docker build`; need to stop and restart multiple times before we finish... Does eventually finish though***
5. DeepDive & Greenplum will now run in the background; to open up a shell again, run:

		docker exec -ti deepdive bash
		
  *Note: this may take a while to start, as it waits for GreenPlum first...*


[deepdiverepo]: https://github.com/hazyresearch/deepdive
[deepdivedocs]: http://deepdive.stanford.edu/index.html#documentation
[mindtagger]: https://github.com/netj/mindbender
[braindump]: https://github.com/zifeishan/braindump
[postgres-pg-static]: https://github.com/postgres/postgres/blob/master/src/include/catalog/pg_statistic.h
[localhost]: http://localhost:8000
[docker-install]: https://docs.docker.com/installation/#installation
[dockerfile-1]: https://gist.github.com/adamwgoldberg/7075b2237f819483a067
[dd-extractors]: http://deepdive.stanford.edu/doc/basics/extractors.html
