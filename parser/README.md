### Parser

A simple XML / HTML parser for pulling out document sections, with some markdown-esque preservation of xml/html tags.

To run end-to-end along with NLP preprocessing using the bazaar lib, make sure the `BAZAAR_DIR` variable and run options are set correctly in `run.sh`, then run:
  
    ./get_deps.sh
    ant
    ./run.sh [XML DIRECTORY OR FILE]

#### To-do:
* Clean up run script
* Parse document metadata
* Parallelize XML parsing?
