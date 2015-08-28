package parser.config;

import javax.xml.stream.XMLStreamReader;

import parser.objects.XMLElement;
import parser.objects.XMLPattern;

public class PlosConfig extends XMLDocConfig {

  public boolean isDocIdSection(XMLStreamReader parser, int xmlStreamConstant) {
    XMLPattern pattern = new XMLPattern(docIdSection, "pmid", null);
    XMLElement element = new XMLElement(parser, xmlStreamConstant);
    return pattern.matches(element);
  }

  public String formatDocId(String docIdText) {
    return docIdText.replace("/", ".");
  }

  public String cleanup(String doc) {
    String out = doc.replaceAll("\\s{2,}", " ");

    // Deal with stuff left after removal of <xref> tags
    out = out.replaceAll("\\s+(\\s|\\(|\\)|,|-|–)*\\.", ".");

    out = out.replaceAll("\\s+,", ",");
    return out;
  }

  public PlosConfig() {
    readSections.put(new XMLPattern("article-title", false), "Title");
    readSections.put(new XMLPattern("abstract", false), "Abstract");
    readSections.put(new XMLPattern("body", false), "Body");
    dataSections.put(new XMLPattern("ref-list", false), "References");
    dataSections.put(new XMLPattern("ref", false), "Reference");
    dataSections.put(new XMLPattern("pub-id", false), "PubId");
    dataSections.put(new XMLPattern("pub-date", false), "Metadata");
    dataSections.put(new XMLPattern("journal-meta", false), "Metadata");
    dataSections.put(new XMLPattern("year", false), "JournalYear");
    dataSections.put(new XMLPattern("journal-title", false), "Journal");
    dataSections.put(new XMLPattern("article", false), "BlockMarker");

    // <issn pub-type="ppub">0028-0836</issn><issn
    // pub-type="epub">1476-4687</issn>
    dataSections.put(new XMLPattern("issn", "pub-type", "ppub"), "ISSNPrint");
    dataSections.put(new XMLPattern("issn", "pub-type", "epub"), "ISSNElectronic");
    // <journal-id journal-id-type="nlm-journal-id">0410462</journal-id>
    dataSections.put(new XMLPattern("journal-id", "journal-id-type", "nlm-journal-id"), "NlmID");

    String[] skipSections = { "title", "xref", "table-wrap", "table", "object-id", "label", "caption", "ext-link" };
    addSkipSections(skipSections);

    String[] splitSections = { "p", "div", "li", "ref" };
    addSplitSections(splitSections);

    String[] splitTags = { "surname" };
    addSplitTags(splitTags);

    markdown.put("bold", "**");
    markdown.put("b", "**");
    markdown.put("strong", "**");
    markdown.put("italic", "_");
    markdown.put("i", "_");
    markdown.put("em", "_");
    markdown.put("underline", "_");
    markdown.put("u", "_");
    markdown.put("br", " ");
    markdown.put("hr", " ");

    docIdSection = "article-id";
  }

  // currently unused here
  public boolean isStartBlock(String localName) {
    return false;
  }

  public boolean isEndBlock(String localName) {
    return false;
  }

}
