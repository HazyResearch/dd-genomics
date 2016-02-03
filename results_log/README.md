## Logging Folder
This folder contains logs from runs for reproducibility.


## Evaluate the current implementation

Go to your `$GDD_HOME`, the application root directory and run `./evaluation.sh $RELATION $VERSION [$CONFIDENCE] [$OPTOUT]` where :
  - $RELATION can be either one of {gene,causation,association} 
  - $VERSION refers to the holdout set version to use for evaluation (starting from 0)
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
