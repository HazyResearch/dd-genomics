# The Genomics DeepDive (GDD) Project

We have a wiki for this project at
<http://dev.stanford.edu/confluence/display/collaborators/DeepDive+Genomics>


## Getting Started: Basics

### 1. Installing DeepDive
*TODO...*

[*See [*DeepDive main documentation*][deepdivedocs] for more detail]* 

### 2. Setting environment variables:
In env.sh, change the variables marked as 'todo' as appropriate for intended usage.  Additional notes:

* ***Mac OSX***: Will need to either install coreutils (e.g. with Homebrew: `brew install coreutils`) or hardcode absolute path; see env.sh
* Most scripts in GDD will call env.sh automatically, but if not, run `bash source env.sh` in the terminal session being used.  (Note that env.sh must be set as executable, `chmod +x env.sh`)


## Basic Structure of GDD
*TO-DO...*


## Running an Iteration of DeepDive
*TO-DO...*


## Running Simple Analyses

After an iteration of DeepDive has been run, some simple analyses (just SQL queries + optional post-processing) can be computed for error analysis and assesment, in addition to the automatically produced calibration plots.  To perform an analysis run:
> ```
> ./analysis/run-analysis.sh [NAME] [MODE]
> ```

where "NAME" is "g", "p" or "gp" (as relevant).  To see a list of available "MODE" arguments (analyses), just run the above with no arguments.

### 1. Current analyses available:

* **mentions-by-source**: Number of mentions of *$NAME* grouped by journal source, with counts broken down by *labeled\_true / labeled\_false / bucket_n*, where e.g. *bucket\_3* is the count of unlabeled mentions with infered expectation between 0.3 and 0.4
* **mentions-by-entity**: Number of mentions of *$NAME* grouped by entity, with same columns as above.  A post-processing step checks for any entities that are in the relevant dictionary but *not* in the table, and includes these with zero counts.  *[Note: the post-processing step doesn't work for phenotypes because the entity names are not yet resolved enough to match with our dictionary...]*
* **relations-by-entity**: Number of relations involving an entity *E*, grouped by *E*, with same columns as above.
* *postgres-stats*: The set of basic statistics compiled automatically by postgres "ANALYZE" operation for query planning.  This data is automatically compiled by postgres during DeepDive execution and thus has no cost for us to get here!  Generates several output csv files labeled by column id and analysis type, e.g. *output\_2\_histogram.csv* would be a histogram of values for column 2 of the *$NAME\_mentions* table.  See [*postgres documentation*][postgres-pg-static] for all analysis types

[*NOTE: gp relations not currently run on raiders4*]

[*NOTE: We want to put these scripts into [*BrainDump*][braindump] / a new UI soon...*]

### 2. Creating new analyses:
The basic structure of an analysis script is:

* an `input-sql.sh` script that takes e.g. $1 \in {gene\_mentions, pheno\_mentions, genepheno\_relations} as an argument and outputs the SQL to run
* [optionally] a `process.py` post-processing script which takes in the input filename, output path root and table name argument as above as inputs.  Exs: Unpacking & splitting data; filling in zero-values from dictionary; etc.

Other analyses we want (TODO):

* Compute ratio of mentions to relations by entity in one single script?
* Something around average mentions/doc?
* *Something involving common features (think about this more algorithmically / generally- longer term)*


## Performing Labeling & Data Inspection Tasks

Having analyzed the output of DeepDive using the calibration plots, analysis scripts described above, and other means, you may want to inspect and/or label specific examples to improve the system.  We use a GUI tool called [*Mindtagger*][mindtagger] to expedite the labeling tasks necessary for evaluating the data products of DeepDive.

### 1. Using Mindtagger to label data

Provided are a set of *templates* for e.g. precision, recall labeling tasks.  First, create a new task by running `./labeling/create-new-task.sh [TASK]` (run without args to view available tasks).  This will create a new output directory in `labeling/` with the mindtagger configuration file and input SQL, and will store the output tags from the labeling done in Mindtagger for this task.  Once tasks are created, run Mindtagger (`./labeling/start-gui.sh`) and then open a browser to [*localhost*][localhost] to view all the created tasks & label data!

### 2. Using Mindtagger to inspect data
*TODO*

### 3. Using Mindtagger tags to supervise DeepDive
*TODO*




## TODOs for next commit (updated: 1/29/15):
*NOTE: run e.g. `grep -r "TODO(alex)" *` to see in-code to-dos by person*

* Get mindtagger gp-recall-highlighted running faster (emailed Jaeho)
* Make simple data inspection mode script for mindtagger with custom SQL query as input
* **Overall GDD documentation (+ pointer to repo on wiki!) -> Finish this!**

[deepdivedocs]: http://deepdive.stanford.edu/index.html#documentation
[mindtagger]: https://github.com/netj/mindbender
[braindump]: https://github.com/zifeishan/braindump
[postgres-pg-static]: https://github.com/postgres/postgres/blob/master/src/include/catalog/pg_statistic.h
[localhost]: http://localhost:8000
