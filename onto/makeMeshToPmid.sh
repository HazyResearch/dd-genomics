#!/bin/bash -e
set -beEu -o pipefail

# Check usage
if [[ $# != 2 ]]; then
    cat 1>&2 <<EOF
$(basename $0) - query NCBI to build a MeSH to PMID table

USAGE
   $(basename $0) meshList.in meshToPmid.out
   
   meshList.in      list of MeSH terms, one per line
   meshToPmid.out   MeSH to PMID links (<MeSH term><TAB><PMID>), one per line
EOF
    exit 1
fi

# Command line parameters
meshListIn=$(readlink -e $1)
meshToPmidOut=$(readlink -f $2)

# Clear/create the output file
touch ${meshToPmidOut} && rm -f ${meshToPmidOut} && touch ${meshToPmidOut}

# Use esearch.fcgi (http://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch) to retrieve
# a list of PMIDs annotation with of the MESH terms in meshList.in.
NCBI_BASE_URL="http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=999999&retmode=json"
while read meshTerm; do
    echo "Searching ${meshTerm}..." 1>&2
    wget -q "${NCBI_BASE_URL}&term=${meshTerm}[MeSH Terms]" -O - |
        jq '.esearchresult.idlist[]' | tr -d '"' | sort -g | uniq |
        awk -v meshTerm="${meshTerm}" '{ print meshTerm "\t" $1; }' |
        tee >(cat >> ${meshToPmidOut}) | awk 'END { print "    " NR " results"; }' 1>&2
done < ${meshListIn}
