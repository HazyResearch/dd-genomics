package parser.config;

import java.util.HashMap;
import javax.xml.stream.XMLStreamReader;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamConstants;

public class PubmedTitlesAbstractsConfig extends XMLDocConfig {
  
  public boolean isDocIdSection(XMLStreamReader parser) {
    if (!parser.getLocalName().equals(docIdSection)) { return false; }
    for (int i=0; i < parser.getAttributeCount(); i++) {
      if (parser.getAttributeValue(i).equals("doi")) { return true; }
    }
    return false;
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

  public PlosTitlesAbstractsConfig() {
    sections.put("ArticleTitle", "Title");
    sections.put("AbstractText", "Abstract");

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

    docIdSection = "article-id";
  }
}
