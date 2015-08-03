package parser.objects;

/**
 * The generic output object. For example this would correspond to one line in
 * the TSV file passed to the NLP pre-processing pipeline (e.g. Bazaar)
 */
public class Section {
  public String docId;
  public String sectionId;
  public String sectionText;
  public String refDocId;

  public Section(String docId, String sectionId, String sectionText) {
    this.docId = docId;
    this.sectionId = sectionId;
    this.sectionText = sectionText;
    this.refDocId = null;
  }

  public Section(String docId, String sectionId, String sectionText, String refDocId) {
    this.docId = docId;
    this.sectionId = sectionId;
    this.sectionText = sectionText;
    this.refDocId = refDocId;
  }
}
