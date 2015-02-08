# The Genomics DeepDive (GDD) Project

We have a wiki for this project at
<http://dev.stanford.edu/confluence/display/collaborators/DeepDive+Genomics>


## Getting Started: Basics

### 1. Installing DeepDive via Docker
***Note that a DeepDive installation is not needed to run the analyses, inspection or labeling tasks (just access to the PSQL database that the results are in)***

*Pending confirmation...:*

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


### 2. Other Docker stuff
* `docker ps -a` to see running containers (should be one for deepdive, one for greenplum)
* To copy file into docker...



[*See [DeepDive main documentation][deepdivedocs] for more detail]* 

### 3. Setting environment variables:
In env.sh, change the variables marked as 'todo' as appropriate for intended usage.  Additional notes:

* ***Mac OSX***: Will need to either install coreutils (e.g. with Homebrew: `brew install coreutils`) or hardcode absolute path; see env.sh
* Most scripts in GDD will call env.sh automatically, but if not, run `bash source env.sh` in the terminal session being used.  (Note that env.sh must be set as executable, `chmod +x env.sh`)

## Running an Iteration of DeepDive
*TO-DO...*


## Basic Contents of this Repository

At a high level, this repo consists of the **"UDF" (User Defined Functions)** and ***"extractors"*** more generally, which output **candidates**, **features** and **distantly-supervised examples** for the core DeepDive system to utilize; plus some additional analysis & labeling code for use on the resulting output.

For the core DeepDive code see [this repo][deepdiverepo].

In more detail, this repo contains:

1. **The `application.conf` file:**  This is the primary configuration file for the core DeepDive system.  In it we define:
	
	* ***Extractors:*** For candidates, features and distantly-supervised examples
	* ***Pipelines:*** Ordered sets of extractors & other operations to execute
	* ***Schema:*** Defining the random variables (RVs) that we are observing / trying to predict
	* ***Inference rules:*** Factors in the factor graph, which define causal relations between RVs in our schema
2. **The extractor code (`code/ext_*`)**: see this [documentation][dd-extractors] also.  These are UDF scripts used by the extractors (note that formally, the extractors are defined in application.conf, and may not require any UDF scripts) that generate the requisite inputs for DeepDive:

	* ***ext\_gene\_find\_acronyms:*** Extracts acronyms, used for distantly supervising the gene mention classification
	* ***ext\_{gene | pheno | genepheno}\_candidates:*** Generates candidate mentions
	* ***ext\_{gene | pheno | genepheno}\_features:*** Outputs the features for candidate mentions

3. **Analysis, inspection & labeling scripts:** See the following sections


## Database Schema

Not an exhaustive list, but important tables:

* ***sentences***: The pre-processed input text, with one row for each sentence
* ***sentences_input***: Same as *sentences*, except arrays stored as strings (for convenience in certain processing steps)
* ***{gene\_mentions | pheno\_mentions | genepheno\_relations}***: The extracted candidates (`is_correct=NULL`) and distantly- or directly-supervised examples (`is_correct=true|false`)
* ***{gene | pheno | genepheno}_features***: Separate tables for features for each of the candidate mentions/relations
* ***{gene\_mentions | pheno\_mentions | genepheno\_relations}\_is\_correct\_inference[\_bucketed]***: Views of the results of the DeepDive run [bucketed by 0.1 increments in expectation value]
* ***acronyms***: Extracted gene acronyms, used for distant supervision
* ***labeled\_gp***: Labeled GP relations (from ...?) for direct supervision of GP relations
* TODO: expand this list...

*NOTE: "pheno" is replaced by "hpoterm" in older datasets...*

Postgres tips:

* `\d+`: See all tables
* `\d+ TABLE_NAME`: See the schema of a specific table *TABLE_NAME*
* `\q`: Exit
* `psql -U $DBUSER -h $DBHOST -p $DBPORT $DBNAME`: Open postgres client


## Running Simple Analyses of Output

After an iteration of DeepDive has been run, some simple analyses (just SQL queries + optional post-processing) can be computed for error analysis and assesment, in addition to the automatically produced calibration plots.  To perform an analysis run:

	./analysis/run-analysis.sh NAME MODE

where `NAME` is "g", "p" or "gp" (as relevant).  To see a list of available `MODE` arguments (analyses), just run the above with no arguments.

### 1. Current analyses available:

* **mentions-by-source**: Number of mentions of *NAME* grouped by journal source, with counts broken down by *labeled\_true / labeled\_false / bucket_n*, where e.g. *bucket\_3* is the count of unlabeled mentions with infered expectation between 0.3 and 0.4
* **mentions-by-entity**: Number of mentions of *NAME* grouped by entity, with same columns as above.  A post-processing step checks for any entities that are in the relevant dictionary but *not* in the table, and includes these with zero counts.  *[Note: the post-processing step doesn't work for phenotypes because the entity names are not yet resolved enough to match with our dictionary...]*
* **relations-by-entity**: Number of relations involving an entity *E*, grouped by *E*, with same columns as above.
* ***postgres-stats***: Compiled by postgres automatically for query planning (only reason we included).  Generates files labeled by column id and analysis type, e.g. *output\_2\_most_common_values.csv* would be the most common values for column 2 of the *NAME\_mentions* table.  See [postgres documentation][postgres-pg-static]

[*NOTE: gp relations not currently run on raiders4*]


### 2. Creating new analyses:
The basic structure of an analysis script is:

* an `input-sql.sh` script that takes e.g. $1 \in {gene\_mentions, pheno\_mentions, genepheno\_relations} as an argument and outputs the SQL to run
* [optionally] a `process.py` post-processing script which takes in the input filename, output path root and table name argument as above as inputs.  Exs: Unpacking & splitting data; filling in zero-values from dictionary; etc.

Other analyses we might want (TODO):

* Compute ratio of mentions to relations by entity in one single script?
* Something around average mentions/doc?
* *Something involving common features (think about this more algorithmically / generally- longer term)*


## Performing Labeling & Data Inspection Tasks

Having analyzed the output of DeepDive using the calibration plots, analysis scripts described above, and other means, you may want to inspect and/or label specific examples to improve the system.  We use a GUI tool called [*Mindtagger*][mindtagger] to expedite the labeling tasks necessary for evaluating the data products of DeepDive.

### 1. Using Mindtagger to inspect data
To inspect certain documents without wanting to label them- e.g. to get some quick intuition about a specific slice of the data while building feature extractors- run:

	./inspection/inspect-data.sh SQL_FILE
	
where `SQL_FILE` is your .sql query for getting the documents you want to inspect.  This will fetch the data and start the Mindtagger GUI.  See example queries in the `inspection/scripts` directory, or just run the above command with no arguments to list available ones.

### 2. Using Mindtagger to label data

Provided are a set of Mindtagger labeling templates for e.g. precision, recall labeling tasks.  First, create a new task by running

	./labeling/create-new-task.sh TASK

(run without args to view available tasks).  This will create a new output directory in `labeling/` where the output tags from the labeling will be stored.  Once all tasks are created, start the Mindtagger GUI by running:

	./labeling/start-gui.sh

and then open a browser to [localhost][localhost] to view all the created tasks & label data!

### 3. Using Mindtagger tags to supervise DeepDive
*TODO*


## Questions (updated: 2/1/15):
For documenting better, or just to look into...

* [Alex] Does DeepDive formally distinguish between distantly- and directly-supervised examples?
* [Alex] Mention : Entity :: Relation : ??
* [Alex] Why do we create unsupervised copies of the labeled examples / is this a good idea?
* [Alex] What are the '_copies' factors about?
* [Alex] How did the skip-chain CRF (now commented out) perform?


## TODOs (updated: 2/1/15):
Ordered from smallest to largest.  *NOTE: To see more minor code-level to-dos, run e.g. `grep -r "TODO(alex)" *`*


* [Alex] Certain analyses scripts taking a really long time (on raiders2):
	* mentions-by-entity
* [Jaheo/Alex] Mindtagger stuff: speed up gp-recall-labeled, fix some errors, export of tags to database
* [Alex/Ragini] Install & run DeepDive! --> Document this
* [Ragini/Alex] Write more analysis & inspection scripts
* **[Ragini/Alex] Iterate on Extractors!**
* **[Alex/Ragini] ENTITY-LINKING**
* ***[Mike/Jaeho/Alex] Replace all of these annoying analysis / inspection scripts with a UI / unified workflow 'Dashboard'***

[deepdiverepo]: https://github.com/hazyresearch/deepdive
[deepdivedocs]: http://deepdive.stanford.edu/index.html#documentation
[mindtagger]: https://github.com/netj/mindbender
[braindump]: https://github.com/zifeishan/braindump
[postgres-pg-static]: https://github.com/postgres/postgres/blob/master/src/include/catalog/pg_statistic.h
[localhost]: http://localhost:8000
[docker-install]: https://docs.docker.com/installation/#installation
[dockerfile-1]: https://gist.github.com/adamwgoldberg/7075b2237f819483a067
[dd-extractors]: http://deepdive.stanford.edu/doc/basics/extractors.html
