#This file create the pipelines defined in pipelines.txt
#The syntax of pipelines.txt has to be name_pipeline: function_1, function_2,..., function_n.

import re

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
      list_elt_pipeline=str_pipeline.split(":")[1].split(",")
      list_elt_pipeline = [i.strip() for i in list_elt_pipeline]
      list_pipelines.append((name_pipeline, list_elt_pipeline))

list_code_pipelines =[]  
for name, list_elt in list_pipelines:
      list_code_py = []
      for name_extractor in list_elt:
            if "#" not in name_extractor:
                  cont = True
                  found=False
                  str_extracted_ddlog = ""
                  with open("./app.ddlog") as ddlog: 
                        for line in ddlog:
                              if cont:
                                    if "function " + name_extractor+ " " in line:
                                          found=True
                                    if found:
                                          str_extracted_ddlog += line
                                          if "." in str_extracted_ddlog:
                                                cont = False
                                                list_code_py.append(line.split('"')[1].strip())
                  if not found:
                        print "error: extractor " + name_extractor + " not found"
      list_code_pipelines.append((name, list_code_py))

print list_code_pipelines



# for i in list_pipelines:
#       print i[0] + " ; "
#       print i[1]