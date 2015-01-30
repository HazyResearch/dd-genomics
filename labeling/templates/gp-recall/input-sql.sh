#!/usr/bin/env bash
set -eu

# default doc_id
[[ $# -gt 0 ]] || set -- journal.pbio.1001475.pdf

# create a list of doc_ids
# TODO which is supposed to be sampled in a rigorous way
ids=
for id; do
    ids+=",''${id//\'/\'\'\'\'}''"
done
ids=${ids#,}

# produce SQL query
echo '
\set doc_id_to_sample '"'($ids)'"'
'"

COPY (

    SELECT doc_id, sent_id, words
      FROM sentences
     WHERE doc_id IN :doc_id_to_sample

) TO STDOUT WITH CSV HEADER
;
"
