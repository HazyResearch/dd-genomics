#!/bin/bash -e

#Here we assume that the ddlog database is accessible by "deepdive sql" so correctly defined in db.url

if [ $# -ne 1 ]; then
	echo "$0: ERROR: wrong number of arguments" >&2
	echo "$0: USAGE: $0 DB" >&2
	exit 1
fi

cd ..
deepdive sql """DROP VIEW IF EXISTS gene_mentions_filtered_is_correct_inference CASCADE;
CREATE VIEW gene_mentions_filtered_is_correct_inference AS SELECT
g.*,
ginf.category as category, 
ginf.expectation as expectation
from gene_mentions_filtered g,
gene_mentions_filtered_inference_label_inference ginf
where ginf.mention_id = g.mention_id;"""

deepdive sql """DROP VIEW IF EXISTS genepheno_causation_is_correct_inference CASCADE;
CREATE VIEW genepheno_causation_is_correct_inference AS SELECT
g.*,
ginf.category as category, 
ginf.expectation as expectation
from genepheno_causation g,
genepheno_causation_inference_label_inference ginf
where ginf.relation_id = g.relation_id;"""

deepdive sql """DROP VIEW IF EXISTS genepheno_association_is_correct_inference CASCADE;
CREATE VIEW genepheno_association_is_correct_inference AS SELECT
g.*,
ginf.category as category, 
ginf.expectation as expectation
from genepheno_association g,
genepheno_association_inference_label_inference ginf
where ginf.relation_id = g.relation_id;"""
