#!/bin/bash

for i in 1 10 100 1000 10000; do
  eval "./run-stability-test.sh 1000 $i 1 infer"
done
