package parser.config;

import javax.xml.stream.XMLStreamReader;

import parser.objects.XMLElement;
import parser.objects.XMLPattern;

public class PubmedTitlesAbstractsConfig extends XMLDocConfig {

  public boolean isDocIdSection(XMLStreamReader parser, int xmlStreamConstant) {
    XMLElement element = new XMLElement(parser, xmlStreamConstant);
    XMLPattern pattern = new XMLPattern(docIdSection, false);
    return pattern.matches(element);
  }

  public String formatDocId(String docIdText) {
    // return docIdText.replace("/", ".");
    return docIdText;
  }

  public String cleanup(String doc) {
    String out = doc.replaceAll("\\s{2,}", " ");

    // Deal with stuff left after removal of <xref> tags
    out = out.replaceAll("\\s+(\\s|\\(|\\)|,|-|–)*\\.", ".");

    out = out.replaceAll("\\s+,", ",");
    return out;
  }

  public PubmedTitlesAbstractsConfig() {
    readSections.put(new XMLPattern("ArticleTitle", false), "Title");
    readSections.put(new XMLPattern("AbstractText", false), "Abstract");
    dataSections.put(new XMLPattern("Journal", false), "Metadata"); // that's right ---
                                                             // the
    // metadata section is
    // called "Journal" in
    // pubmed files
    dataSections.put(new XMLPattern("ISOAbbreviation", false), "Journal");
    dataSections.put(new XMLPattern("Year", false), "JournalYear");
    dataSections.put(new XMLPattern("MedlineCitation", false), "BlockMarker");
    dataSections.put(new XMLPattern("ISSNLinking", false), "ISSNGlobal");
    dataSections.put(new XMLPattern("NlmUniqueID", false), "NlmID");
    // <ISSN IssnType="Electronic">1553-2712</ISSN>
    // <ISSN IssnType="Print">0363-5023</ISSN>
    dataSections.put(new XMLPattern("ISSN", "IssnType", "Electronic"), "ISSNElectronic");
    dataSections.put(new XMLPattern("ISSN", "IssnType", "Print"), "ISSNPrint");

    String[] skipSections = {};
    addSkipSections(skipSections);

    String[] splitSections = {};
    addSplitSections(splitSections);

    String[] splitTags = {};
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

    docIdSection = "PMID";
  }

}
