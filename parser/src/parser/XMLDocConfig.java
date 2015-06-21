package parser;

import java.util.HashMap;
import java.util.HashSet;
import java.util.ArrayList;

public class XMLDocConfig {

  /**
   * The flat sections to pull out of the doc and output as individual files
   */
  private HashMap<String, String> sections = new HashMap<String, String>();

  protected void addSection(String section, String name) { sections.put(section, name); }

  public boolean getSection(String section) { return sections.containsKey(section); }

  public String sectionName(String section) { return sections.get(section); }


  /**
   * Elements to completely skip over (for now at least)
   */
  private HashSet<String> skipSections = new HashSet<String>();

  protected void addSkipSections(String[] skips) { 
    for (String skip : skips) { skipSections.add(skip); }
  }

  public boolean skipSection(String section) { return skipSections.contains(section); }


}
