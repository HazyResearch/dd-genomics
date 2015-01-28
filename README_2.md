# The Genomics DeepDive (GDD) Project

We have a wiki for this project at
<http://dev.stanford.edu/confluence/display/collaborators/DeepDive+Genomics>


## Getting Started: Basics

### 1. Installing DeepDive
See [*DeepDive main documentation*][deepdivedocs]

### 2. Setting environment variables:
In env.sh, change the variables marked as 'todo' as appropriate for intended usage.  Additional notes:

* ***Mac OSX***: Will need to either install coreutils (e.g. with Homebrew: `brew install coreutils`) or hardcode absolute path; see env.sh
* Most scripts in GDD will call env.sh automatically, but if not, run `bash source env.sh` in the terminal session being used.  (Note that env.sh must be set as executable, `chmod +x env.sh`)


## Basic Structure of GDD
*TO-DO...*


## Running an Iteration of DeepDive
*TO-DO...*


## Running Simple Analyses

[*NOTE: We want to put these scripts into [*BrainDump*][braindump] eventually, and/or iteratively make this process smoother and more user friendly...*]

After an iteration of DeepDive has been run, various metrics can be computed for error analysis and assesment, in addition to the automatically produced calibration plots.  For some examples, see the scripts in the metrics/ directory:

### 1. Current analyses available:
*Where X = {g, p, gp}*

* **X-stats-basic**: The set of basic statistics compiled automatically by postgres "ANALYZE" operation for query planning.  This data is automatically compiled by postgres during DeepDive execution and thus has no cost for us to get here!  Generates several output csv files labeled by column id and analysis type, e.g. *output_2_histogram.csv* would be a histogram of values for column 2 of the *X_mentions* table.  See [*postgres documentation*][postgres-pg-static] for all analysis types

### 2. Ideas for analyses / TODO:
* Subsample set of g/p from dict and get counts from db (fast?)
* Can we get the total set of counts in a fast enough way (need to index?)
* General histogram based on ANALYZE command
* g + p -> g,p analyses (done per doc to be faster)
* By journal (group by)


## Performing Labeling & Data Inspection Tasks

Having analyzed the output of DeepDive using the calibration plots, analysis scripts described above, and other means, you may want to inspect and/or label specific examples to improve the system.  We use a GUI tool called [*Mindtagger*][mindtagger] to expedite the labeling tasks necessary for evaluating the data products of DeepDive.

### 1. Launching Mindtagger

To start the GUI tool, simply run:
```bash
  ./run-mindtagger.sh
```

and open a browser to "http://localhost:8000".

The GUI shows, in the upper left corner, all tasks defined under `labeling/` directory.
The results of the labeling (including intermediate data) are stored under each task directory.

[deepdivedocs]: http://deepdive.stanford.edu/index.html#documentation
[mindtagger]: https://github.com/netj/mindbender
[braindump]: https://github.com/zifeishan/braindump
[postgres-pg-static]: https://github.com/postgres/postgres/blob/master/src/include/catalog/pg_statistic.h
