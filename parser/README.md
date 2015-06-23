### Parser

A simple XML / HTML parser for pulling out document sections, with some markdown-esque preservation of xml/html tags.

To use:
  
    ant
    java -ea -jar parser.jar [FILE OR DIRECTORY] > output.tsv

The output is a TSV file where each line is the document ID (one for each section extracted) and then the document text, which can be fed directly into the NLP preprocessing parser e.g. bazaar.
