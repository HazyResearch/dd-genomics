### Labeling data:

**[Labeling guidelines](https://docs.google.com/document/d/1z16_Rnmoi5iZ2A80zWxG8FpPVlaib6rM_kswL74HGQs/edit?usp=sharing)**

#### Prerequisites:
1. Make sure your env_local.sh is correctly setup in the application root directory
2. Make sure the table of interest is correctly populated. If not, populate it using `deepdive do ..` command. For example: use `deepdive do gene_mentions` if you'd like to label gene mentions

#### Prepare & launch Mindtagger:
**Basic**: You can start labeling in two basic steps:
	
Run `./start_mindtagging $MENTION [$LABELER_NAME]`: The first argument is required to generate the right hold-out set (gene/pheno/genepheno). The second argument is optional: if none is given, the script will use the `$DDUSER` based on your `env_local.sh`. This script will generate the corresponding hold-out set for your relation, choose an unused port number and launch MindTagger on it. 

**Advanced**: If you wish to customize the labeling pipeline, for instance to have a specific port number, perform the following steps.
	
1. Generate adequate hold-out set (`create_new_[g|p|gp]_holdout_set.sh [$LABELER_NAME]`): This script generates a hold-out set for a given relation (g: genes, p: phenotypes, gp: genepheno). The argument is optional: if none is given, the script will use the `$DDUSER` based on your `env_local.sh`.
2. Choose a port number: for example `export PORT=6593`
3. Fire Mindtagger: `./start-gui.sh`
	
NOTE: Running a new mindtagger task will automatically store the old ones under 'OLD/' for backup. They are ignored by the gitignore.

#### Export tags:
Run `export_labels.sh $MENTION [$LABELER_NAME]`: the arguments are similar to the above. This script will load all the non-null labels to the shared database using the version saved in 'version\_labeling' file and update your label\_backup file in `labels/$RELATION_$LABELER_NAME`. To move to the next version for holdout set, you have to update 'version\_labeling'.
Note that you should consistently use the names if you decide to personalize the `$LABELER_NAME` variable.

NOTE: When exporting the labels, we also store them as shared backup in 'labels/$RELATION_$LABELER_NAME'. These backups are shared through git and should not cause any conflict assuming that the same labeler works from the same machine or commits when working from a different one.

#### Access Labels
Labels are stored on Raiders7 on Greenplum. The database is called genomics_labels and contains 3 tables:
- gene_labels
- pheno_labels
- genepheno_labels

All three tables have the following schema:
mention_id (or relation_id for genepheno), is_correct, labeler

#### Import labels to DeepDive SQL
To compute the precision, or withhold labeled data from being distance supervised, we need to import the shared labels in the DeepDive database. We provide two ways to do it:
1- run `import_labels.sh`
2- run `deepdive redo genepheno_causation_labels` for causation labels. This is done automatically when you run the Deepdive pipeline from the beginning.

#### Get Precision and Recall Numbers

To output the precision and recall stats for a relation, say genepheno\_causation, run the corresponding `./compute_causation_stats.sh [$CONFIDENCE]`. This computes the precision, recall and F1 score and stores them in `stats_causation.tsv`. `$CONFIDENCE` is an optional argument (default: 0.9) to represent the threshold for inference: if the `expectation > $CONFIDENCE`, we classify the relation as true. Otherwise, we classify it as false.

Similarly, run `./compute_association_stats.sh [$CONFIDENCE]`, `./compute_gene_stats.sh [$CONFIDENCE]` for association and gene stats respectively.

