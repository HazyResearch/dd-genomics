#! /bin/bash

cp dicts/english_words.tsv data/english_words.tsv

# Download and parse HPO term list (with synonyms and graph edges)
RAW="raw/hpo.obo"
if [ ! -e "$RAW" ]; then
	wget http://compbio.charite.de/hudson/job/hpo/lastStableBuild/artifact/hp/hp.obo -O "$RAW"
fi
python parse_hpo.py "$RAW" data/hpo_phenotypes.tsv
python gen_hpo_dag.py > data/hpo_dag.tsv

# Download and parse HPO disease annotations (DECIPHER, OMIM, ORPHANET mapped to HPO)
# http://www.human-phenotype-ontology.org/contao/index.php/annotation-guide.html
# output format: <disease DB, disease ID, disease name, synonyms, HPO IDs>
# http://stackoverflow.com/questions/23719065/tsv-how-to-concatenate-field-2s-if-field-1-is-duplicate
RAW="raw/hpo_phenotype_annotation.tsv"
if [ ! -e "$RAW" ]; then
	wget http://compbio.charite.de/hudson/job/hpo.annotations/lastStableBuild/artifact/misc/phenotype_annotation.tab -O "$RAW"
fi
awk -F'\t' 'p==$1$2$3$12 {printf "|%s", $5;next}{if(p){print ""};p=$1$2$3$12;printf "%s\t%s\t%s\t%s\t%s", $1,$2,$3,$12,$5}END{print ""}' "$RAW" > data/hpo_disease_phenotypes.tsv
awk -F'\t' '{printf "%s:%s\t%s\n", $1, $2, $3}' data/hpo_disease_phenotypes.tsv | grep 'DECIPHER:' > data/diseases_deci.tsv

# Download OMIM for disease names
if [ ! -e "raw/omim.txt" ]; then
	wget ftp://ftp.omim.org/OMIM/omim.txt.Z -O raw/omim.txt.Z
	uncompress raw/omim.txt.Z
fi
python parse_omim.py raw/omim.txt data/diseases_omim.tsv

# clinvar diseases
CLINVAR_DISEASES="data/diseases_clinvar.tsv"
RAW="raw/clinvar_diseases.tsv"
if [ ! -e "$RAW" ]; then
	wget ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/disease_names -O "$RAW"
fi
awk -F'\t' '{printf "%s\t%s\n", $3, $1}' "$RAW" | tail -n +2 | sort | uniq | awk -F'\t' 'p==$1 && p {printf "|%s", $2;next} {if(!$1) $1="L"NR} {if(started){print ""};p=$1;started=1;printf "CLINVAR:%s\t%s", $1,$2}END{print ""}' > data/diseases_clinvar.tsv

# DO diseases
DO_DISEASES="data/diseases_do.tsv"
RAW="raw/HumanDO.obo"
if [ ! -e "$RAW" ]; then
	wget http://sourceforge.net/p/diseaseontology/code/HEAD/tree/trunk/HumanDO.obo?format=raw -O raw/HumanDO.obo
fi
python parse_do.py "$RAW" data/diseases_do.tsv

# ORDO
# ORDO has diseases, genes, country names, etc. We take only nodes below children of "phenome".
RAW="raw/ORDO.csv"
if [ ! -e "$RAW" ]; then
	wget "http://data.bioontology.org/ontologies/ORDO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv" -O raw/ORDO.csv.gz
	gunzip raw/ORDO.csv.gz
fi
grep '^http://www.orpha.net/ORDO/' raw/ORDO.csv | \
egrep 'http://www.orpha.net/ORDO/Orphanet_(377790|377796|377792|377788|377795|377794|377797|377789|377791|377793)[^\d]' | \
sed 's#http://www.orpha.net/ORDO/Orphanet_#ORPHANET:#g' | \
python csv2tsv.py | \
awk -F'\t' '{if($3) {$3=$2"|"$3} else {$3=$2}; printf "%s\t%s\n", $1, $3}' > data/diseases_ordo.tsv

# Get disease to gene mapping
RAW="raw/diseases_to_genes.txt"
if [ ! -e "$RAW" ]; then
	wget http://compbio.charite.de/hudson/job/hpo.annotations.monthly/lastStableBuild/artifact/annotation/diseases_to_genes.txt -O "$RAW"
fi
tail -n +2 "$RAW" | awk -F'\t' '{if ($3!="") printf "%s\t%s\n", $1, $3}' | sort > data/hpo_disease_genes.tsv

# get pheno to gene mappings
RAW="raw/ALL_SOURCES_ALL_FREQUENCIES_phenotype_to_genes.txt"
if [ ! -e "$RAW" ]; then
	wget http://compbio.charite.de/hudson/job/hpo.annotations.monthly/lastStableBuild/artifact/annotation/ALL_SOURCES_ALL_FREQUENCIES_phenotype_to_genes.txt -O "$RAW"
fi
tail -n +2 "$RAW" | cut -f1,4 | sort > data/hpo_phenotype_genes.tsv

# Get hgnc to uniprot gene id mappings
RAW="raw/hgnc_to_uniprot_raw.tsv"
if [ ! -e "$RAW" ]; then
  wget 'http://www.genenames.org/cgi-bin/download?col=gd_app_sym&col=md_prot_id&status=Approved&status_opt=2&where=&order_by=gd_app_sym_sort&format=text&limit=&hgnc_dbtag=on&submit=submit' -O "$RAW"
fi
tail -n +2 "$RAW" | sort > data/hgnc_to_uniprot.tsv

# Get Reactome data
## Uniprot ID, Reactome ID, pathway name
RAW="raw/reactome_uniprot_raw.tsv"
if [ ! -e "$RAW" ]; then
  wget http://www.reactome.org/download/current/UniProt2Reactome.txt -O "$RAW"
fi
awk -F '\t' '$6 == "Homo sapiens"' "$RAW" | cut -f1,2,4 > data/reactome_uniprot.tsv
## Reactome pathway hierarchy
RAW="raw/reactome_hierarchy_raw.tsv"
if [ ! -e "$RAW" ]; then
  wget http://www.reactome.org/download/current/ReactomePathwaysRelation.txt -O "$RAW"
fi
cp "$RAW" data/reactome_hierarchy.tsv
python gen_reactome_db.py > data/reactome_db.tsv

# Get gene list
cp dicts/merged_genes_dict.tsv data/genes.tsv

# Run disease dictionary merge script
python merge_diseases.py data

# get gene to pmid mappings
RAW="raw/gene2pubmed.gz"
if [ ! -e "$RAW" ]; then
  wget ftp://ftp.ncbi.nih.gov/gene/DATA/gene2pubmed.gz -O "$RAW"
fi
RAW="raw/gene2ensembl.gz"
if [ ! -e "$RAW" ]; then
  wget ftp://ftp.ncbi.nih.gov/gene/DATA/gene2ensembl.gz -O "$RAW"
fi
# grab all the pmids that have less than 5 gene annotations since other genes have too many mappings for us to reasonably assess (gene collection papers, gwas, etc.)
gzip -dc raw/gene2pubmed.gz | awk '{if($1==9606) print $2"\t"$3}' |
 sort -u  | cut -f2 | sort | uniq -c | awk '{if($1<=5) print $2}' | sort -u |
 join -t$'\t' -j 1 /dev/stdin <(gzip -dc raw/gene2pubmed.gz | awk '{if($1==9606) print $3"\t"$2}' | sort -u) |
 sort -k2,2 |
 join -t$'\t' -1 2 -2 1 /dev/stdin <(gzip -dc raw/gene2ensembl.gz | awk '{if($1==9606) print $2"\t"$3}' | sort -u) |
 cut -f2- | sort -u -o data/pmid_to_ensembl.tsv


## Make the ENSEMBL gene maps files
# 
set -beEu -o pipefail

# Starting from a table of: ENSEMBL_ID | canonical HGNC gene symbol | refseq ID
	# Further note: filtered for protien-coding only
	# filtered to be only from the main chromosomes (not from any of the 'PATCH' sequence files or similar on ensembl biomart
if [ ! -f dicts/mart_export.txt ]; then
	echo " No biomart file found! Downloading."
	# Downloads a biomart file with columns: ensembl_ID | HGNC gene symbol | refseq_ID
	wget -O dicts/mart_export.txt 'http://www.biomart.org/biomart/martservice?query=%3C?xml%20version=%221.0%22%20encoding=%22UTF-8%22?%3E%3C!DOCTYPE%20Query%3E%3CQuery%20%20virtualSchemaName%20=%20%22default%22%20formatter%20=%20%22TSV%22%20header%20=%20%220%22%20uniqueRows%20=%20%220%22%20count%20=%20%22%22%20datasetConfigVersion%20=%20%220.6%22%20%3E%3CDataset%20name%20=%20%22hsapiens_gene_ensembl%22%20interface%20=%20%22default%22%20%3E%3CFilter%20name%20=%20%22chromosome_name%22%20value%20=%20%221,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT%22/%3E%3CFilter%20name%20=%20%22biotype%22%20value%20=%20%22protein_coding%22/%3E%3CAttribute%20name%20=%20%22ensembl_gene_id%22%20/%3E%3CAttribute%20name%20=%20%22hgnc_symbol%22%20/%3E%3CAttribute%20name%20=%20%22refseq_mrna%22%20/%3E%3C/Dataset%3E%3C/Query%3E' 
fi

# Also starting with a table of: gene symbol | gene synonyms (separated by a pipe | between each) | full gene name
if [ ! -f dicts/hugo_export.txt ]; then
	echo " No HUGO gene symbol/synonym file found! Downloading from genenames.org."
	# Downloads a biomart file with columns: HGNC gene symbol | HGNC gene synonyms (separated by commas)
	wget -O dicts/hugo_export.txt 'http://www.genenames.org/cgi-bin/download?title=HGNC+output+data&hgnc_dbtag=on&col=gd_app_sym&col=gd_prev_sym&col=gd_aliases&col=gd_pub_acc_ids&col=md_eg_id&status=Approved&status_opt=2&level=pri&=on&where=&order_by=gd_app_sym_sort&limit=&format=text&submit=submit&.cgifields=&.cgifields=level&.cgifields=chr&.cgifields=status&.cgifields=hgnc_dbtag' 
fi

# Make a table of: ENSEMBL_ID | canonical gene symbol
cut -f 1-2 dicts/mart_export.txt | sort | uniq | grep ENSG | awk '{ print $1":"$2 "\t" $2 }' > dicts/ensembl_symbols.txt 

# Make a table of: gene symbol | gene synonyms (separated by a pipe between each)
cat dicts/hugo_export.txt | tail -n+2 | awk 'FS="\t" {print $1 "\t" $3}' | sed -e 's/, /|/g' >  dicts/symbols_syns.txt

# Make a table of: ENSEMBL ID | gene symbol | gene synonym
awk 'NR==FNR {h[$1] = $2; next} { print $1, $2, h[$2] }' dicts/symbols_syns.txt dicts/ensembl_symbols.txt > dicts/ensembl_symbols_syns.txt 

# Make a table of: ENSEMBL IDs | gene synonym | type (always the string "NON-CANONICAL_SYMBOL")       (one line per relationship)
cat dicts/ensembl_symbols_syns.txt | awk '{if($3!=""){n=split($3,a,"|");for(i=1;i<=n;i++){ print $1 "\t" a[i] "\t" "NONCANONICAL_SYMBOL"}}  }' > dicts/ensembl_syns.txt

# Make a table of: ENSEMBL ID | canonical gene symbol | type (always the string "CANONICAL_SYMBOL")
cat dicts/ensembl_symbols.txt | awk '{ print $0 "\t" "CANONICAL_SYMBOL" }' > dicts/ensembl_symbols_canonical.txt

#OPTIONAL: remove all entries with a blank symbol listed as a canonical gene name
cat dicts/ensembl_symbols_canonical.txt | grep -E '[\d]*:[a-zA-Z0-9]' > temp.txt
mv temp.txt dicts/ensembl_symbols_canonical.txt

# Make a table of: ENSEMBL_ID | refseq ID | type (always the string "REFSEQ")
cat dicts/mart_export.txt | awk '{if(NF==3) print $1":"$2 "\t" $3 "\t" "REFSEQ" }' | grep NM_ | sort | uniq > dicts/ensembl_refseq.txt

# Make a table of: ENSEMBL_ID | ENSEMBL_ID (without the cannonical gene symbol appended after a colon) | type (always the string "ENSEMBL ID")
cut -f 1-2 dicts/mart_export.txt | sort | uniq | grep ENSG | awk '{ print $1":"$2 "\t" $1 "\t" "ENSEMBL_ID" }' > dicts/ensembl_direct.txt 

# Combine ensembl_refseq.txt, ensembl_symbols_canonical.txt, and ensembl_syns.txt to make a table of:
# ENSEMBL ID | (symbol, synonym, refseq id) | type identifier (CANONICAL_SYMBOL, NON-CANONICAL_SYMBOL, REFSEQ)
cat dicts/ensembl_refseq.txt dicts/ensembl_symbols_canonical.txt dicts/ensembl_syns.txt dicts/ensembl_direct.txt | sort | uniq > dicts/ensembl_map.tsv

# OPTIONAL: remove all entries with phrase length of 1 or 2 (no one- or two-letter genes) 
#cat dicts/ensembl_map.tsv | awk '{if(length($2)>2){print $0}}' > temp.txt
#mv temp.txt dicts/ensembl_map.tsv	

# OPTIONAL: delete all intermediate files
rm dicts/ensembl_refseq.txt
rm dicts/ensembl_direct.txt
rm dicts/ensembl_symbols.txt
rm dicts/ensembl_symbols_canonical.txt
rm dicts/ensembl_symbols_syns.txt
rm dicts/ensembl_syns.txt
rm dicts/symbols_syns.txt

# Copy the final table to the data folder for use by deepdive
cp dicts/ensembl_map.tsv data/ensembl_genes.tsv

# Get mesh terms that map to phenotypes in HPO
cut -d $'\t' -f 7 data/hpo_phenotypes.tsv  | sort -u | tail -n +2 > data/meshList.txt

# Get mesh to pubmed ID map
if [ ! -f data/meshToPmid.tsv ]; then
  if [ -f /lfs/raiders2/0/robinjia/data/meshToPmid.tsv ]; then
    cp /lfs/raiders2/0/robinjia/data/meshToPmid.tsv data/meshToPmid.tsv
  else
    echo " Copying meshToPmid.tsv from local filesystem failed."
    echo " If have access to raiders2, run scp username@raiders2:/lfs/raiders2/0/robinjia/data/meshToPmid.tsv data/meshToPmid.tsv"
    echo " Otherwise, use ./makeMeshToPmid.sh to re-generate file by querying PubMed."
    echo " Then, re-run this script."
    exit 1
  fi
fi

# Join to get HPO to pubmed ID map through MeSH
join -t $'\t' -1 2 -2 1 -o 1.1,2.2 <(cut -f1,7 data/hpo_phenotypes.tsv | egrep -v $'\t''$' | sort -k2) data/meshToPmid.tsv > data/hpo_to_pmid_via_mesh.tsv

# Get map between PMIDs and DOIs.
RAW="raw/PMC-ids.csv"
if [ ! -e "$RAW" ]; then
  wget ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz -O - | gzip -dc > $RAW
fi
# Extract plos DOIs that map to pubmed IDs.
OUT="data/plos_doi_to_pmid.tsv"
if [ ! -e "$OUT" ]; then
  tail -n +2 raw/PMC-ids.csv | grep -i plos | cut -d ',' -f8,10 | tr ',' '\t' | grep -v $'\t''$' > "$OUT"
fi

# Deploy the "phrase to ENSEMBL" map
bzip2 -cd manual/phrase_to_ensembl.tsv.bz2 > data/phrase_to_ensembl.tsv

# Get EntrezID to ENSEMBL ID mapping

if [ ! -f dicts/entrez2ensembl.txt ]; then
	echo " No entrez to ensembl map found! Downloading."
	# Downloads a biomart file with columns: ENTREZ_ID | ENSEMBL_ID
	wget -O dicts/entrez_raw.txt 'http://www.biomart.org/biomart/martservice?query=%3C%3Fxml%20version%3D%221.0%22%20encoding%3D%22UTF-8%22%3F%3E%0A%3C!DOCTYPE%20Query%3E%0A%3CQuery%20%20virtualSchemaName%20%3D%20%22default%22%20formatter%20%3D%20%22TSV%22%20header%20%3D%20%220%22%20uniqueRows%20%3D%20%220%22%20count%20%3D%20%22%22%20datasetConfigVersion%20%3D%20%220.6%22%20%3E%0A%09%09%09%0A%09%3CDataset%20name%20%3D%20%22hsapiens_gene_ensembl%22%20interface%20%3D%20%22default%22%20%3E%0A%09%09%3CAttribute%20name%20%3D%20%22entrezgene%22%20%2F%3E%0A%09%09%3CAttribute%20name%20%3D%20%22ensembl_gene_id%22%20%2F%3E%0A%09%3C%2FDataset%3E%0A%3C%2FQuery%3E'
	# Remove all ENSEMBL IDs which do not also have an associated ENTREZ ID
	cat dicts/entrez_raw.txt | awk '{if(NF>=2){print $0}}' > dicts/entrez2ensembl.txt
	echo "Converting entrez_raw.txt to entrez2ensembl.txt."
	rm dicts/entrez_raw.txt
fi
