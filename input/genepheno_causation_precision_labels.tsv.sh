#! /usr/bin/env bash

psql -U $DDUSER -p 6432 -d genomics_labels -c "COPY (SELECT * FROM genepheno_causation_precision_labels) TO STDOUT WITH NULL AS ''"
