package parser;

import parser.config.XMLDocConfig;

import java.io.InputStream;
import java.io.FileInputStream;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamReader;
import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class XMLDocParser {
  private InputStream xmlStream;
  private XMLInputFactory factory;
  private XMLStreamReader parser;
  private XMLDocConfig config;

  private void skipSection(String localName) {
    try {
      for (int e = parser.next(); e != XMLStreamConstants.END_DOCUMENT; e = parser.next()) {
        if (e == XMLStreamConstants.END_ELEMENT && parser.getLocalName().equals(localName)) {
          break;
        }
      }
    } catch (XMLStreamException ex) {
      System.out.println(ex);
    }
  }

  private String getFlatElementText(String elementName) {
    StringBuilder section = new StringBuilder();
    String localName;
    try {
      loop: for (int e = parser.next(); e != XMLStreamConstants.END_DOCUMENT; e = parser.next()) {
        switch (e) {
          case XMLStreamConstants.CHARACTERS:
            section.append(parser.getText());
            break;

          case XMLStreamConstants.END_ELEMENT:
            localName = parser.getLocalName();
            if (parser.getLocalName().equals(elementName)) {
              break loop; 
            } else if (config.isSplitSection(localName)) {
              if (section.length() > 0 && section.charAt(section.length()-1) != '.') { 
                section.append("."); 
              }
              section.append(" ");
            } else if (config.isSplitTag(localName)) {
              section.append(" ");
            } else if (config.isMarkdown(localName)) {
              section.append(config.getMarkdown(localName));
            }
            break;

          case XMLStreamConstants.START_ELEMENT:
            localName = parser.getLocalName();
            if (config.isSkipSection(localName)) {
              skipSection(localName);
            } else if (config.isMarkdown(localName)) {
              section.append(config.getMarkdown(localName));
            }
            break;
        }
      }
      return config.cleanup(section.toString());
    } catch (XMLStreamException ex) {
      System.out.println(ex);
      return "";
    }
  }

  /**
   * Go through the XML document, pulling out certain flat sections as individual output files.
   */
  public ArrayList<OutputDoc> parse() {
    HashSet<String> seenNames = new HashSet<String>();
    String docId = null;
    ArrayList<OutputDoc> outDocs = new ArrayList<OutputDoc>();
    try {
      parser = factory.createXMLStreamReader(this.xmlStream);
      while (true) {
        int event = parser.next();
        if (event == XMLStreamConstants.START_ELEMENT) {
          String localName = parser.getLocalName();

          // Try to get the doc id
          if (docId == null && config.isDocIdSection(parser)) {
            docId = config.formatDocId(getFlatElementText(localName));

          // get sections that are in scope
          } else if (config.isInScope(localName)) {
            assert docId != null;
            String docName = docId + "." + config.getSectionName(localName);
            if (seenNames.contains(docName)) { docName = iterateName(docName); }
            seenNames.add(docName);
            OutputDoc outDoc = new OutputDoc(docName, getFlatElementText(localName));
            outDocs.add(outDoc);
          }
        } else if (event == XMLStreamConstants.END_DOCUMENT) {
          parser.close();
          break;
        }
      }
    } catch (XMLStreamException ex) {
      System.out.println(ex);
    }
    return outDocs;
  }

  private String iterateName(String name) {
    Pattern p = Pattern.compile("\\d+$");
    Matcher m = p.matcher(name);
    int num = 1;
    if (m.find()) { num = Integer.parseInt(m.group()) + 1; }
    return name + "." + Integer.toString(num);
  }

  /**
   * Parses and outputs the XML document's metadata
   */
  public void getMetadata() {
    // TODO
  }

  // Default constructor from InputStream
  public XMLDocParser(InputStream xmlStream, XMLDocConfig config) {
    this.xmlStream = xmlStream;
    this.factory = XMLInputFactory.newInstance();
    this.config = config;
  }
}
