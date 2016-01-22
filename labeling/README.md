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
	
#### Export tags:
Run `export_tags.sh $MENTION [$LABELER_NAME]`: the arguments are similar to the above. This script will load all the non-null labels to the shared database and update your label_backup file in `labels/$RELATION_$LABELER_NAME`.
Note that you should consistently use the names if you decide to personalize the `$LABELER_NAME` variable.

#### Get Precision and Recall Numbers

#### Access Labels
Labels are stored on Raiders7 on Greenplum. The database is called genomics_labels and contains 3 tables:
- gene_labels
- pheno_labels
- genepheno_labels

All three tables have the following schema:
mention_id (or relation_id for genepheno), is_correct, labeler
