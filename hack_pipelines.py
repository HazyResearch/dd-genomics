#!/usr/local/bin/python

#This file create the pipelines defined in pipelines.txt
#The syntax of pipelines.txt has to be name_pipeline: function_1, function_2,..., function_n.

import re
import subprocess

with open("./pipelines.txt") as file_pipeline:
      list_string_pipeline=[]
      string_pipeline = ''
      for line in file_pipeline:
            line = line.strip()
            if line != '':
                  string_pipeline += line
                  if '.' in line:
                        list_string_pipeline.append(string_pipeline.replace(".", ""))
                        string_pipeline = ''

list_pipelines=[]
for str_pipeline in list_string_pipeline:
      name_pipeline = str_pipeline.split(":")[0].strip()
      list_elt_pipeline_temp=str_pipeline.split(":")[1].split(",")
      list_elt_pipeline = []
      for i in list_elt_pipeline_temp:
            if "#" not in i:
                  list_elt_pipeline.append(i.strip())
      list_pipelines.append((name_pipeline, list_elt_pipeline))


print list_pipelines

#Launching the load pipeline
idx_load = 0
for i in list_pipelines:
      if list_pipelines[idx_load][0] == 'load_pipeline':
            for name_table_load in list_pipelines[idx_load][1]:
                  try:
                        subprocess.call(['input/init_'+name_table_load+'.sh'])
                  except:
                        print 'input/init_'+name_table_load+'.sh was not found'
            list_pipelines = list_pipelines[:idx_load] + list_pipelines[(idx_load +1):]
            break
      else:
            idx_load+=1
if idx_load >= len(list_pipelines):
      print "load_pipeline not found"


#Launching the cleanup pipeline
idx_cleanup = 0
for i in list_pipelines:
      if list_pipelines[idx_cleanup][0] == 'cleanup_doc_pipeline':
            for name_table_load in list_pipelines[idx_cleanup][1]:
                  try:
                        subprocess.call(['input/'+name_table_load+'.sh'])
                  except:
                        print 'input/init_'+name_table_load+'.sh was not found'
            list_pipelines = list_pipelines[:idx_cleanup] + list_pipelines[(idx_cleanup +1):]
            break
      else:
            idx_cleanup+=1
if idx_cleanup >= len(list_pipelines):
      print "cleanup_doc_pipeline not found"

#Add the pipeline in a deepdive.conf file
#Actually, according to jahoe, the deepdive.conf file can contain only the new pipeline since a run of deepdive will compile app.ddlog
# if list_pipelines

print list_code_pipelines