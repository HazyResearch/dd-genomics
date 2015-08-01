package parser.objects;

/**
 * The generic output object. For example this would correspond to one line in
 * the TSV file passed to the NLP pre-processing pipeline (e.g. Bazaar)
 */
public class OutputDoc {
    public String docName;
    public String docText;

    public OutputDoc(String docName, String docText) {
        this.docName = docName;
        this.docText = docText;
    }
}
