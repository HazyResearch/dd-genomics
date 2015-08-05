### Parser

A simple XML / HTML parser for pulling out document sections, with some markdown-esque preservation of xml/html tags.  This is run as the first component of the end-to-end preprocessing:

1. **XML parsing [this lib]**
2. NLP preprocessing [bazaar / coreNLP]
3. Loading into db [psql]

To install and compile, run:

    ./get_deps.sh
    ant

To run end-to-end, make sure the `BAZAAR_DIR`, `PARALLELISM` and db variables are set correctly in `dd-genomics/env_local.sh`, then run, specifying whether to add to an existing table or create one:
  
    ./run.sh [In: a directory of / single xml file] [out: db table] ["create"|"add"]

#### To-do:
* Parse document metadata
* Parallelize XML parsing?

### Notes (bazaar):
* Testing pmc.json on raiders (80 cores): 80k lines in 20m ~= 250K/hr
* Testing pmc.json on an ec2-m3.large (2 cores): 10K lines in 15m ~= 40K/hr
* *Testing pmc.json on an ec2-c3.4xlarge (16 cores): 80k lines in 15m ~= 300K/hr*
  * Memory errors... seems like the ratio of memory:cores too low?
* Testing pmc.json on **two** ec2-m3.2xlarges (2 x 8 cores): 80k lines in 26m ~= 200K/hr
