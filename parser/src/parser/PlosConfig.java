package parser;

import java.util.HashMap;

public class PlosConfig extends XMLDocConfig {

  public PlosConfig() {
    addSection("article-title", "Title");
    addSection("abstract", "Abstract");
    addSection("body", "Body");
    addSection("ref-list", "References");
    String[] skipSections = {"title", "xref", "table-wrap", "table", "object-id", "label", "caption", "ext-link"};
    addSkipSections(skipSections); 
  }
}
