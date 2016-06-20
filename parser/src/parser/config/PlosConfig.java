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
    //out = out.replaceAll("\\([^a-zA-Z0-9]*\\)", "");
    //out = out.replaceAll("\\[[^a-zA-Z0-9]*\\]", "");

    //out = out.replaceAll("\n", " ");

    out = out.replaceAll("[ ]{2,}", " ");

    out = out.replaceAll("\\s+,", ",");
    out = out.replaceAll("\\s+\\.", ".");
    
    return out;
  }

  public PlosConfig() {
    headerSections.put(new XMLPattern("article-title", false), "Title");
    headerSections.put(new XMLPattern("abstract", false), "Abstract");
    readSections.put(new XMLPattern("body", false), "Body"); 
    readSections.put(new XMLPattern("sec", false), "Section");
    readSections.put(new XMLPattern("title", false), "SectionTitle");
    dataSections.put(new XMLPattern("ref-list", false), "References");
    dataSections.put(new XMLPattern("ref", false), "Reference");
    dataSections.put(new XMLPattern("pub-id", false), "PubId");
    dataSections.put(new XMLPattern("pub-date", false), "Metadata");
    dataSections.put(new XMLPattern("journal-meta", false), "Metadata");
    dataSections.put(new XMLPattern("year", false), "JournalYear");
    dataSections.put(new XMLPattern("journal-title", false), "Journal");
    dataSections.put(new XMLPattern("article", false), "BlockMarker");
    dataSections.put(new XMLPattern("xref",false), "Xref");
    dataSections.put(new XMLPattern("kwd-group",false), "Metadata");
    dataSections.put(new XMLPattern("kwd", false), "Keyword");
    dataSections.put(new XMLPattern("article-categories",false), "Metadata");
    dataSections.put(new XMLPattern("subj-group", false), "Heading");
    dataSections.put(new XMLPattern("contrib", false), "Metadata");
    dataSections.put(new XMLPattern("name", false), "AuthorName");
    dataSections.put(new XMLPattern("aff", false), "Affiliation");
    

    // <issn pub-type="ppub">0028-0836</issn><issn
    // pub-type="epub">1476-4687</issn>
    dataSections.put(new XMLPattern("issn", "pub-type", "ppub"), "ISSNPrint");
    dataSections.put(new XMLPattern("issn", "pub-type", "epub"), "ISSNElectronic");
    // <journal-id journal-id-type="nlm-journal-id">0410462</journal-id>
    dataSections.put(new XMLPattern("journal-id", "journal-id-type", "nlm-journal-id"), "NlmID");

    String[] skipSections = { "table-wrap", "table", "object-id", "label", "caption", "ext-link" };
    addSkipSections(skipSections);

    String[] splitSections = { "p", "div", "li", "ref" };
    addSplitSections(splitSections);

    String[] splitTags = { "surname" };
    addSplitTags(splitTags);

    //markdown.put("bold", "**");
    //markdown.put("b", "**");
    //markdown.put("strong", "**");
    //markdown.put("italic", "_");
    //markdown.put("i", "_");
    //markdown.put("em", "_");
    //markdown.put("underline", "_");
    //markdown.put("u", "_");
    //markdown.put("br", " ");
    //markdown.put("hr", " ");

    markdown.put("bold", "");
    markdown.put("b", "");
    markdown.put("strong", "");
    markdown.put("italic", "");
    markdown.put("i", "");
    markdown.put("em", "");
    markdown.put("underline", "");
    markdown.put("u", "");
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
