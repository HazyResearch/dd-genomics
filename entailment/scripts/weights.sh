#!/bin/bash
source ../env_local.sh
psql -X --set ON_ERROR_STOP=1 -d ${DBNAME} -c 'SELECT * FROM dd_inference_result_weights_mapping'
