#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")"

: ${GDD_SENTENCES_FILE:=../../genomics_sentences_10k.tsv}
cat "$GDD_SENTENCES_FILE" |
# WARNING: After loading, pay attention if ref_doc_id and sent_id in sentences is flipped!
#          This apparently happens sporadically. If it's the case, flip the dollar4 and dollar3 in the load_sentences script
awk -F '\t' '{OFS="\t"; print $1, $2, $4, '\N', $5, $6, $7, $8, $9, $10}'
