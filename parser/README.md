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
