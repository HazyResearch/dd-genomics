
# Download and parse HPO term list (with synonyms and graph edges)

wget http://compbio.charite.de/hudson/job/hpo/lastStableBuild/artifact/hp/hp.obo -O raw/hpo.obo
python parse_hpo.py raw/hpo.obo data/hpo_phenotypes.tsv

# Download and parse HPO disease annotations (DECIPHER, OMIM, ORPHANET mapped to HPO)
# http://www.human-phenotype-ontology.org/contao/index.php/annotation-guide.html
# output format: <disease DB, disease ID, disease name, synonyms, HPO IDs>
# http://stackoverflow.com/questions/23719065/tsv-how-to-concatenate-field-2s-if-field-1-is-duplicate

wget http://compbio.charite.de/hudson/job/hpo.annotations/lastStableBuild/artifact/misc/phenotype_annotation.tab -O raw/hpo_phenotype_annotation.tsv
awk -F'\t' 'p==$1$2$3$12 {printf "|%s", $5;next}{if(p){print ""};p=$1$2$3$12;printf "%s\t%s\t%s\t%s\t%s", $1,$2,$3,$12,$5}END{print ""}' raw/hpo_phenotype_annotation.tsv > data/hpo_disease_phenotypes.tsv

# Get more disease names
awk -F'\t' '{printf "%s:%s\t%s\n", $1, $2, $3}' data/hpo_disease_phenotypes.tsv | grep 'DECIPHER:' > data/diseases_deci.tsv

wget ftp://ftp.omim.org/OMIM/omim.txt.Z -O raw/omim.txt.Z
uncompress raw/omim.txt.Z
python parse_omim.py raw/omim.txt data/diseases_omim.tsv

wget ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/disease_names -O raw/clinvar_diseases.tsv
awk -F'\t' '{printf "%s\t%s\n", $3, $1}' raw/clinvar_diseases.tsv | tail -n +2 | sort | uniq | awk -F'\t' 'p==$1 && p {printf "|%s", $2;next} {if(!$1) $1="ClinVar"NR} {if(started){print ""};p=$1;started=1;printf "%s\t%s", $1,$2}END{print ""}' > data/diseases_clinvar.tsv

wget http://sourceforge.net/p/diseaseontology/code/HEAD/tree/trunk/HumanDO.obo?format=raw -O raw/HumanDO.obo
python parse_do.py raw/HumanDO.obo data/diseases_do.tsv


wget "http://data.bioontology.org/ontologies/ORDO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv"l -O raw/ORDO.csv.gz
gunzip raw/ORDO.csv.gz

# ORDO has diseases, genes, country names, etc. We take only nodes below children of "phenome".

grep '^http://www.orpha.net/ORDO/' raw/ORDO.csv | \
egrep 'http://www.orpha.net/ORDO/Orphanet_(377790|377796|377792|377788|377795|377794|377797|377789|377791|377793)[^\d]' | \
sed 's#http://www.orpha.net/ORDO/Orphanet_#ORPHANET:#g' | \
python csv2tsv.py | \
awk -F'\t' '{if($3) {$3=$2"|"$3} else {$3=$2}; printf "%s\t%s\n", $1, $3}' > data/diseases_ordo.tsv


# Get relations to genes
wget http://compbio.charite.de/hudson/job/hpo.annotations.monthly/lastStableBuild/artifact/annotation/diseases_to_genes.txt -O raw/diseases_to_genes.txt

tail -n +2 raw/diseases_to_genes.txt | awk -F'\t' '{if ($3!="") printf "%s\t%s\n", $1, $3}' | sort > data/hpo_disease_genes.tsv

wget http://compbio.charite.de/hudson/job/hpo.annotations.monthly/lastStableBuild/artifact/annotation/ALL_SOURCES_ALL_FREQUENCIES_phenotype_to_genes.txt -O raw/ALL_SOURCES_ALL_FREQUENCIES_phenotype_to_genes.txt

tail -n +2 raw/ALL_SOURCES_ALL_FREQUENCIES_phenotype_to_genes.txt | cut -f1,4 | sort > data/hpo_phenotype_genes.tsv


# Get gene list
wget https://github.com/HazyResearch/dd-genomics/raw/master/dicts/merged_genes_dict.tsv -O raw/merged_genes_dict.tsv
cp raw/merged_genes_dict.tsv data/genes.tsv

python merge_diseases.py data
