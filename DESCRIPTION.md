# DeepDive Genomics Application Description

Last Update: 20141201

This document describes the Genomics applications built on top of DeepDive. We
present the schema of the database tables and the various extractors for gene,
phenotypes, and gene/phenotypes relations, and how they interact with each
other.

## Input

The input is a set of scientific articles crawled from the web and processed
using the Stanford CoreNLP toolkit. The results of the processing are stored in
the `sentences` table and for convenience, in the `sentences_input` table. Each
row in these table corresponds to one sentence. The schemas for the `sentences`
table can be found in `code/schema.sql`. The `sentences_input` table has a
different schema in that arrays are transformed into strings (`text` type) with
values separated by `|^|`. The motivation for having the `sentences_input` table
is that we would transforms arrays into strings anyway for each extractor which
uses the `sentences` table, so it is convenient to do it once and for all.

## Extractors

The extractors are defined in the `application.conf` file and are all either
`tsv_extractor`s or `sql_extractor`s. The UDF scripts for the `tsv_extractor`s
are in the `code` directory.

### find_acronyms

The `find_acronyms` extractor is a `tsv_extractor` whose UDF is the
`code/find_acronyms.py` script. The input of the extractor are whole documents,
obtained by grouping the appropriate rows of the `sentences_input` table. The
output goes to the `acronyms` table, whose schema is:

```
      Table "static.acronyms"
   Column    |  Type   | Modifiers
-------------+---------+-----------
 doc_id      | text    |
 acronym     | text    |
 definitions | text[]  |
 is_correct  | boolean |
 ```

The role of this extractor is to detect and classify acronyms defined in the
document. The `is_correct` boolean describes whether one of the definition for
the `acronym` is a long name for a gene or not. In some cases, when we are
uncertain, the `is_correct` column contains a `NULL` value. The rules for the
choice of the value can be found in the `code/find_acronyms.py` script.
Intuitively, we avoid making a call if the definition is not a long name for a
gene but contains one of a set of keywords (e.g., "protein", "gene", "factor")
which are usually referred to genes. This field is used for distant supervision. 

### extract_gene_mentions

The `extract_gene_mentions` extractor is a `tsv_extractor` whose UDF is the
`code/extract_gene_mentions.py` script. The input are single sentences from the
`sentences_input` table. The output goes to the `gene_mentions` table, whose
schema is:
 
```
     Table "public.gene_mentions"
   Column   |   Type    | Modifiers
------------+-----------+-----------
 id         | bigint    |
 doc_id     | text      |
 sent_id    | integer   |
 wordidxs   | integer[] |
 mention_id | text      |
 type       | text      |
 entity     | text      |
 words      | text[]    |
 is_correct | boolean   |
 features   | text[]    |
```

The role of this extractor is to create candidates for gene mentions, add
features to them, and perform some distant supervision. The rules for features
and for distant supervision can be found in the `code/extract_gene_mentions.py`
script.

### gene_supervision_acronyms

The `gene_supervision_acronyms` extractor is a `sql_extractor` which updates
some rows in the `gene_mentions` table using information from the `acronyms`
table. As such, the extractor depends on the `extract_gene_mentions` and
`find_acronyms` extractors. The extractor joins the `gene_mentions` and
`acronyms` table on the `doc_id` column and on `gene_mentions.words[1] =
acronyms.acronym`, and set the `gene_mentions.is_correct` column to the value in
the `acronyms.is_correct` column (provided the former is `NULL`).

### add_unsuper_dup_genes

This is a `sql_extractor` extractor which creates unsupervised copies of
supervised gene candidates. It depends on the `gene_supervision_acroynyms`
extractor and, for technical reasons, on the `gene_hpoterm_relations` extractor.

### extract_geneRifs_mentions

This is a `tsv_extractor` which create supervised gene mentions candidate from
the GeneRIFs sentences, which acts like a labelled dataset. The input comes from
the `generifs` table, which has the same schema as the `sentences` table, except
for an additional column `gene` which contains the gene symbol which is known to
be in the sentence. The output is stored in the `generifs_mentions` table, whose
schema is the same as the `gene_mentions` table. The extractor UDF is
`code/extract_geneRifs_mentions.py`, which basically acts like the
`code/extract_gene_mentions.py` script (it actually calls functions in it) and
supervises the candidates as `True`.

### add_geneRifs_mentions

This is a `sql_extractor` which adds the contents of the `generifs_mentions`
table to the `gene_mentions` table. It depends on the
`extract_geneRifs_mentions` extractor and on the `add_unsuper_dup_genes`
extractor (so that we do not create duplicated unsupervised mentions for these,
which are not useful).

### extract_hpoterm_mentions

This is a `tsv_extractor` whose input is the `sentences_input` table (i.e., one
sentence at a time), and whose UDF script is `code/extract_hpoterm_mentions.py`.
The output goes to the `hpoterm_mentions` relation whose schema is the same as
the `gene_mentions` table. This extractor creates candidate phenotype mentions,
adds features to them, and performs distant supervision.

### add_unsuper_dup_hpoterms

This is the same as the `add_unsuper_dup_genes` extractor but for phenotypes
mentions.

### gene_phenotype_relations

This is a `tsv_extractor`. The input is a sentence from the `sentences_input`
table together with the sets of gene mention candidates and of phenotype mention
candidates from the same sentence. This extractor depends on the
`supervise_gene_acronyms` and `extract_hpoterm_mentions` extractors. The UDF
script is `code/gene_phenotype_relations.py` and the output goes to the
`gene_phenotype_relations` table, whose schema is

```
Table "public.gene_hpoterm_relations"
    Column    |   Type    | Modifiers
--------------+-----------+-----------
 id           | bigint    |
 doc_id       | text      |
 sent_id_1    | integer   |
 sent_id_2    | integer   |
 relation_id  | text      |
 type         | text      |
 mention_id_1 | text      |
 mention_id_2 | text      |
 wordidxs_1   | integer[] |
 wordidxs_2   | integer[] |
 words_1      | text[]    |
 words_2      | text[]    |
 is_correct   | boolean   |
 features     | text[]    |
 ```

 The role of this extractor is to create gene/phenotype relation candidates, add
 features, and perform supervision. For each pair of gene and phenotype found in
 the sentence, a candidate is created. The supervision uses the existing HPO
 mapping to label positive candidates, while negative candidates are created by
 looking at the labels for the gene and phenotypes mentions composing the
 relation. 

### add_unsuper_dup_hpoterms

This is the same as the `add_unsuper_dup_genes` extractor but for
gene/phenotype relation candidates.
