#! /bin/bash

cat input_schema.sql | sed 's/DISTRIBUTED BY (.*);/;/g' > input_schema_psql.sql
cat schema.sql | sed 's/DISTRIBUTED BY (.*);/;/g' > schema_psql.sql
