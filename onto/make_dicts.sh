
# Download and parse HPO term list (with synonyms and graph edges)
RAW="raw/hpo.obo"
if [ ! -e "$RAW" ]; then
	wget http://compbio.charite.de/hudson/job/hpo/lastStableBuild/artifact/hp/hp.obo -O "$RAW"
fi
python parse_hpo.py "$RAW" data/hpo_phenotypes.tsv

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
awk -F'\t' '{printf "%s\t%s\n", $3, $1}' "$RAW" | tail -n +2 | sort | uniq | awk -F'\t' 'p==$1 && p {printf "|%s", $2;next} {if(!$1) $1="ClinVar"NR} {if(started){print ""};p=$1;started=1;printf "%s\t%s", $1,$2}END{print ""}' > data/diseases_clinvar.tsv

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
	wget "http://data.bioontology.org/ontologies/ORDO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv"l -O raw/ORDO.csv.gz
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

# Get gene list
cp dicts/merged_genes_dict.tsv data/genes.tsv

# Run disease dictionary merge script
python merge_diseases.py data
