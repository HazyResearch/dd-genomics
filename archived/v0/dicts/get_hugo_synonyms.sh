#! /bin/sh
#
# Update the hugo_synonyms.tsv file by downloading and preprocessing the last
# version from Hugo
#

# URL to download the Hugo map from
HUGO_MAP_URL="http://www.genenames.org/cgi-bin/hgnc_downloads?title=HGNC+output+data&hgnc_dbtag=on&col=gd_app_sym&col=gd_prev_sym&col=gd_aliases&col=gd_pub_acc_ids&col=md_eg_id&status=Approved&status_opt=2&level=pri&=on&where=&order_by=gd_app_sym_sort&limit=&format=text&submit=submit&.cgifields=&.cgifields=level&.cgifields=chr&.cgifields=status&.cgifields=hgnc_dbtag"

# Download the last version
#FETCH_CMD="wget -O"
FETCH_CMD="fetch -q -o"
HUGO_MAP_FILE="hugo.map"
${FETCH_CMD} ${HUGO_MAP_FILE} ${HUGO_MAP_URL} > /dev/null

# Extract only the fields we are interested in and format them appropriately
# XXX Requires GNU sed
# XXX (Matteo): For historical purposes, and in case someone can't install gsed,
# here's another way of getting (almost?) the same stuff using Mac OS X sed,
# which is what Amir had originally:
#cut -f1,2,3 hugo.map | tr -d "," | grep -i -v withdrawn | tr " " "\t" | sed "s/\t\t/\t/g" | sed 's/	*$//' | sort -u > hugo_synonyms.tsv
if [ `uname` = "Linux" ]; then
	SED="sed"
else
	SED="gsed"
	which $SED > /dev/null 2> /dev/null
	if [ $? -gt 0 ]; then
		echo "This script only work with gsed. Sorry but the sed in OSX is way too cumbersome" >&2
		exit 1
	fi
fi

#cut -f1,2,3 ${HUGO_MAP_FILE} | ${SED} -r -e 's/,[ |\t]*/\t/g' -e 's/\s+/\t/g' -e 's/\t$//g' | grep -i -v withdrawn | sort -u > hugo_synonyms.tsv
cut -f1,2,3 ${HUGO_MAP_FILE} | ${SED} -r -e 's/,[ |\t]*/,/g' -e 's/\s+/,/g' -e 's/,+$//g' -e 's/,/\t/' | grep -i -v withdrawn | sort -u > hugo_synonyms.tsv

# Remove the map file
rm ${HUGO_MAP_FILE}

