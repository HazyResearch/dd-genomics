#! /bin/sh
#
# Link the parser outputs contained in the article directory to a file named
# like the article
#
# First argument is the directory containing the article directories
# Second argument is the directory where the links should be created.

if [ $# -ne 2 ]; then
	echo "$0: ERROR: wrong number of arguments" >&2
	echo "$0: USAGE: $0 INPUT_DIR OUTPUT_DIR" >&2
	exit 1
fi

if [ \( ! -r $1 \) -o \( ! -x $1 \) ]; then
	echo "$0: ERROR: can not traverse input article_filename" >&2
	exit 1
fi

mkdir -p $2

for article_filename in `find $1 -maxdepth 1 -type d`; do
	if [ -r ${article_filename}/input.text ]; then
		if [ ! -r $2/`basename ${article_filename}` ]; then
			ln -s ${article_filename}/input.text $2/`basename ${article_filename}`
		fi
	fi
done

