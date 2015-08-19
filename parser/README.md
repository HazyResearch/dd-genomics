### Parser

This directory contains parsers for extracting document sections from raw formats (e.g. XML, HTML, PDF/OCR, etc.).  The current parser handles XML, preserving formatting tags in markdown syntax, and splitting documents into relevant flat sections.

Each parser should take some input and output a file where each line is a `json` object representing a section of a document, having the following attributes:
* `doc-id`: The ID of a document containing this section (ex: PMID)
* `section-id`: The name / local ID of the section (e.g. "Body.0")
* `ref-doc-id`: The ID of the document referred to by a reference section, else null
* `content`: The content in text format

Where `doc-id.section-id` should be considered the unique object ID.

## Example Preprocessing Pipeline

The below is an example of how to go from raw XML documents to DeepDive-ready database table, using the tools in this directory and the [bazaar](https://github.com/HazyResearch/bazaar) repository

#### Step 1: XML -> JSON Section Objects

First, install and compile the XML parser in this directory:
```bash
./get_deps.sh && ant
```

Given a directory or single file of XML documents, parse them into json section objects:
```bash
./run_parser.sh ${INPUT_DIR} ${INPUT_FORMAT} ${OUT_NAME}
```
Where `INPUT_FORMAT` is currently one of `[pmc, plos, pubmed, abstracts]`- see code for details.  This will output three files: `${OUT_NAME}.json`, `${OUT_NAME}.md.tsv`, and `${OUT_NAME}.om.txt` which are the json section objects, the document metadata, and the error rows (sections with null `doc-id`) respectively.

#### Step 2: JSON -> CoreNLP-Parsed TSV

##### Single machine
Next, use [bazaar](https://github.com/HazyResearch/bazaar) to do NLP-preprocessing of the section objects.  To do so on a single machine, multi-core, in the bazaar directory run e.g.:
```bash
cd parser
./run_parallel.sh -in="${OUT_NAME}.json" --parallelism=8 -i json -k "doc-id,section-id,ref-doc-id" -v "content"
cat ${OUT_NAME}.json.split/*.parsed > ${OUT_NAME}.tsv
rm -rf ${OUT_NAME}.json.split
```
##### Distributed
Or, to run in a distributed fashion in the cloud, use the tools in `bazaar/distribute`.  For example, to run on 20 ec-2 machines in the AWS cloud (we used the `m3.2xlarge` instance type), follow the setup instructions, then run:
```bash
cd distribute
fab launch:cloud=ec2,num=20
fab install > install.log
time fab copy_parse_collect:input=${OUT_NAME}.json,parallelism=8,key_id="doc-id\,section-id\,ref-doc-id",content="content" terminate > parse.log
```
**Note that it is likely that one or more segments will fail to process.**  Use `fab get_status` to see uncompleted segments.  To abort a hanging run, `Ctrl+C` then run `fab collect` to get the processed files, then `fab terminate` to terminate the servers.  Then, debug / re-run problem segments in `segments/` and `cat` with the `result` file.  Finally, to cleanup:
```bash
rm -rf segments/
mv result ${OUT_NAME}.tsv
```

See the READMEs in [bazaar/parser](https://github.com/HazyResearch/bazaar/parser) and [bazaar/distribute](https://github.com/HazyResearch/bazaar/distribute) respectively for more details.

#### Step 3: Load into DB

Load the sentences:
```bash
./load_sentences.sh ${OUT_NAME}.tsv ${SENTENCES_TABLE_NAME} ${OP}
```
where `OP` is `new` or `add` to create or append to the table respectively.  Next, load the metadata:
```bash
./load_md.sh ${OUT_NAME}.md.tsv ${MD_TABLE_NAME} ${OP}
```
Note that in some cases duplicat `(doc_id, section_id, sent_id)` entries may exist between sets.  For example, there is overlap between our PMC and PubMed-Abstracts-Titles sets.  We load each as a new separate table, and then merge, prefering PMC:
```SQL
INSERT INTO sentences s0 (
  SELECT * FROM sentences_pubmed_abs s1 WHERE s1.doc_id NOT IN (
    SELECT DISTINCT(s2.doc_id) FROM sentences s2));
```
