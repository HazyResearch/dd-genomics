package parser;

import java.io.InputStream;
import java.io.FileInputStream;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamReader;
import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamException;
import java.util.ArrayList;

// http://www.xml.com/pub/a/2003/09/17/stax.html
// http://tutorials.jenkov.com/java-xml/sax-example.html
// https://docs.oracle.com/javase/tutorial/jaxp/sax/parsing.html

public class XMLDocParser {
  private InputStream xmlStream;
  private XMLInputFactory factory;
  private XMLStreamReader parser;
  private XMLDocConfig config;

  private void skipSection(String localName) {
    try {
      for (int e = parser.next(); e != XMLStreamConstants.END_DOCUMENT; e = parser.next()) {
        if (e == XMLStreamConstants.END_ELEMENT && parser.getLocalName() == localName) {
          break;
        }
      }
    } catch (XMLStreamException ex) {
      System.out.println(ex);
    }
  }

  // TODO: actually parse text nicely: add spaces in appropriate places, convert B/I/etc -> markdown, etc!
  private String getFlatElementText(String elementName) {
    StringBuilder section = new StringBuilder();
    try {
      for (int e = parser.next(); e != XMLStreamConstants.END_DOCUMENT; e = parser.next()) {
        if (e == XMLStreamConstants.CHARACTERS) {
          section.append(parser.getText());
        } else if (e == XMLStreamConstants.END_ELEMENT && parser.getLocalName() == elementName) {
          break;
        } else if (e == XMLStreamConstants.START_ELEMENT && config.skipSection(parser.getLocalName())) {
          skipSection(parser.getLocalName());
        }
      }
      return section.toString();
    } catch (XMLStreamException ex) {
      System.out.println(ex);
      return "";
    }
  }

  /**
   * Go through the XML document, pulling out certain flat sections as individual output files.
   */
  public ArrayList<OutputDoc> parse() {
    ArrayList<OutputDoc> outDocs = new ArrayList<OutputDoc>();
    try {
      parser = factory.createXMLStreamReader(this.xmlStream);
      while (true) {
        int event = parser.next();
        if (event == XMLStreamConstants.START_ELEMENT) {
          String localName = parser.getLocalName();
          if (config.getSection(localName)) {

            // TODO: get doc id!
            String docId = "DOC_ID";
            String docName = docId + "." + config.sectionName(localName);
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
