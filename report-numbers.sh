echo "Number of documents: " 
deepdive sql """
select count(distinct doc_id) from sentences_input;
"""

echo "Number of documents with body: " 
deepdive sql """
select count(distinct doc_id) from sentences_input where section_id like 'Body%';
"""

echo "Number of sentences: " 
deepdive sql """
select count(distinct *) from sentences_input;
"""

echo "Number of gene objects: "
deepdive sql """
select count(distinct gene_name) from genes where name_type = 'CANONICAL_SYMBOL';
"""

deepdive sql """
select name_type, count(name_type) from genes group by name_type;
"""

echo "How many gene candidates are there in total?"
deepdive sql """
select count(*) from (select distinct * from gene_mentions where gene_name is not null) a;
"""

echo "How many distinct gene objects do we pick up as candidates?"
deepdive sql """
select count(*) from (select distinct g.canonical_name from gene_mentions m join genes g on (m.gene_name = g.gene_name));
"""

echo "How many distinct gene objects does Charite contain?"
deepdive sql """
select count(*) from (select distinct g.canonical_name from charite c join genes g on c.ensembl_id = g.ensembl_id);
"""

deepdive sql """
select mapping_type, count(mapping_type) from (select distinct * from gene_mentions) a group by mapping_type;
"""

echo "How many non-gene-acronym definitions do we pick up?"
deepdive sql """
select count(*) from non_gene_acronyms
"""

echo "How many genes do we supervise false as a result of acronym detection?"
deepdive sql """
select count(*) from gene_mentions where supertype like '%ABBREV%’;
"""

echo "How many 'allowed' (non-cancer) HPO phenotypes do we have?"
deepdive sql """
select count(distinct hpo_id) from allowed_phenos;
"""

echo "How many synonyms for each pheno on average?"
echo "TODO"

echo "How many pheno candidates are there in total?"
deepdive sql """
select count(*) from (select distinct * from pheno_mentions where pheno_entity is not null) a;
"""

echo "How many distinct pheno objects do we pick up as candidates? (non-canonicalized, sorry, I'm going to fix this later)"
deepdive sql """
select count(*) from (select distinct pheno_entity from pheno_mentions) a;
"""

echo "Classification of pheno candidates:"
deepdive sql """
select supertype, count(supertype) from pheno_mentions group by supertype order by count desc;
"""

echo "How many distinct pheno objects does charite contain (... also non-canonicalized)?"
deepdive sql """
select count(distinct hpo_id) from charite;
"""

echo "How many gene name+pheno pairs occur in total single sentences (no random negatives)?"
deepdive sql """
select count(*) from (select gene_name, pheno_entity from genepheno_pairs p join gene_mentions gm on (p.gene_mention_id = gm.mention_id) join pheno_mentions pm on (p.pheno_mention_id = pm.mention_id) where gm.gene_name is not null and pm.pheno_entity is not null) a;
"""

echo "How many distinct gene object+pheno pairs occur in total single sentences (no random negatives)?"
deepdive sql """
select count(*) from (select distinct canonical_name, pheno_entity from genepheno_pairs p join gene_mentions gm on (p.gene_mention_id = gm.mention_id) join pheno_mentions pm on (p.pheno_mention_id = pm.mention_id) join genes g on (gm.gene_name = g.gene_name) where gm.gene_name is not null and pm.pheno_entity is not null) a;
"""

echo "How many gene name+pheno pairs do we subject to inference? (I.e. after all filtering by dependency path distance; after filtering out genes+phenos we CURRENTLY don't like ...)"
deepdive sql """
select count(*) from genepheno_causation;
"""

echo "How does the broad gene distant supervision picture look?"
deepdive sql """
select supertype, count(supertype) from gene_mentions group by supertype order by count desc;
"""

echo "How does the broad pheno distant supervision picture look?"
echo "TODO, this is currently a mess"

echo "How does the broad genepheno causation supervision picture look?"
deepdive sql """
select supertype, count(supertype) from genepheno_causation group by supertype order by count desc;
"""

echo "... association: TODO"

echo "How many features do we extract per genepheno causation candidate on average?"
deepdive sql """
select a.count::float / b.count::float from (select count(*) as count from genepheno_causation c) b, (select count(*) as count from genepheno_features f join genepheno_causation c on (f.relation_id = c.relation_id)) a;
"""

echo "What are the highest weighted features?"
