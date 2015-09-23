#! /bin/bash

cat | sort -u -t$'\t' -k1,1
