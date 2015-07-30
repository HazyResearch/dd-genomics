package parser.config;

import java.util.HashMap;
import java.util.HashSet;
import java.util.ArrayList;
import javax.xml.stream.XMLStreamReader;
import javax.xml.stream.XMLStreamException;

public abstract class XMLDocConfig {

  /**
   * The flat sections to pull out of the doc and output as individual files
   */
  protected HashMap<String, String> sections = new HashMap<String, String>();
  public boolean isInScope(String section) { return sections.containsKey(section); }
  public String getSectionName(String section) { return sections.get(section); }

  /**
   * Elements to completely skip over (for now at least)
   */
  protected HashSet<String> skipSections = new HashSet<String>();
  protected void addSkipSections(String[] skips) { 
    for (String skip : skips) { skipSections.add(skip); }
  }
  public boolean isSkipSection(String section) { return skipSections.contains(section); }

  /**
   * Elements to split at. Ensure that there is a space / period separation.
   */
  protected HashSet<String> splitSections = new HashSet<String>();
  protected void addSplitSections(String[] splits) { 
    for (String split : splits) { splitSections.add(split); }
  }
  public boolean isSplitSection(String section) { return splitSections.contains(section); }

  /**
   * Elements to split at. For inline tags, do not e.g. add a period before.
   */
  protected HashSet<String> splitTags = new HashSet<String>();
  protected void addSplitTags(String[] splits) { 
    for (String split : splits) { splitTags.add(split); }
  }
  public boolean isSplitTag(String tag) { return splitTags.contains(tag); }

  /**
   * Converting html / xml tags to markdown wrappers
   */
  protected HashMap<String, String> markdown = new HashMap<String, String>();
  public boolean isMarkdown(String tag) { return markdown.containsKey(tag); }
  public String getMarkdown(String tag) { return markdown.get(tag); }

  /**
   * Getting the doc id
   */
  protected String docIdSection;
  public abstract boolean isDocIdSection(XMLStreamReader parser);
  public abstract String formatDocId(String docIdText);

  /**
   * Cleanup operations
   */
  public abstract String cleanup(String doc);

  /**
   * Splitting into blocks for PubMed MedlineCitations
   */
  public abstract boolean isStartBlock(String localName);
  public abstract boolean isEndBlock(String localName);
}
