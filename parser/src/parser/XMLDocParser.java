package parser;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Stack;

import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamReader;

import parser.config.XMLDocConfig;
import parser.objects.Metadata;
import parser.objects.Section;
import parser.objects.XMLElement;

public class XMLDocParser {
  private InputStream xmlStream;
  private XMLInputFactory factory;
  private XMLStreamReader parser;
  private XMLDocConfig config;
  private HashSet<String> allTitles;
  private HashSet<String> allPubIds;
  private HashMap<String, Integer> seenNames = new HashMap<String, Integer>();
  private Stack<Section> sectionsStack = new Stack<Section>();
  private Stack<String>  xmlElmntNamesStack = new Stack<String>();
  private ArrayList<Section> sections = new ArrayList<Section>();
  private boolean inBody_Flag = false;
  private boolean read_Flag = false;
  private PrintWriter mdWriter;
  private PrintWriter omWriter;
  private File inputFile;

  private void skipSection(String localName) {
    try {
      for (int e = parser.next(); e != XMLStreamConstants.END_DOCUMENT; e = parser.next()) {
        if (e == XMLStreamConstants.END_ELEMENT && parser.getLocalName().equals(localName)) {
          break;
        }
      }
    } catch (XMLStreamException ex) {
      ex.printStackTrace();
    }
  }

  private boolean getSectionContent(String docId) {
    Section activeSection = this.sectionsStack.peek();
    Section secondSection = null;
    String  activeXMLElmntName = this.xmlElmntNamesStack.peek();
    try {
      loop: for (int e = parser.next(); e != XMLStreamConstants.END_DOCUMENT; e = parser.next()) {
        switch (e) {
        case XMLStreamConstants.CHARACTERS:
          activeSection.content.append(parser.getText());
          break;

        case XMLStreamConstants.END_ELEMENT: {
          XMLElement localElement = new XMLElement(parser, e);
          if (localElement.elementName.equals(activeXMLElmntName)) {
	    // found active sections end_element. Update content and add Section in sections arrylist
	    activeSection = this.sectionsStack.pop();
	    this.xmlElmntNamesStack.pop();
	    if (activeSection.content.length() > 0) {
		activeSection.updateContent(config.cleanup(activeSection.content.toString()));
	    	this.sections.add(activeSection);
            }
	    if (this.sectionsStack.isEmpty()) {
            	break loop;
            }
            else {
		activeSection = this.sectionsStack.peek();
	 	activeXMLElmntName = this.xmlElmntNamesStack.peek();
            }
          } else if (config.isSplitSection(localElement.elementName)) {
            //if (activeSection.content.length() > 0 && activeSection.content.charAt(activeSection.content.length() - 1) != '.') {
            //  activeSection.content.append(".");
            //}
            activeSection.content.append(" ");
          } else if (config.isSplitTag(localElement.elementName)) {
            activeSection.content.append(" ");
          } else if (config.isMarkdown(localElement.elementName)) {
            activeSection.content.append(config.getMarkdown(localElement.elementName));
	  }
          break;
        }

        case XMLStreamConstants.START_ELEMENT: {
          XMLElement localElement = new XMLElement(parser, e);
          if (config.isSkipSection(localElement.elementName)) {
            skipSection(localElement.elementName);
          } else if (config.isMarkdown(localElement.elementName)) {
            activeSection.content.append(config.getMarkdown(localElement.elementName));
          } else if ("SectionTitle".equals(config.getReadSectionName(localElement))) {
	    // grab section title 
	    String title = getFlatElementText(localElement);
	    // update the title only if you are in a section
	    if (!"body".equals(activeXMLElmntName)) {
	    	// grab title of second element and stack titles
	    	activeSection = this.sectionsStack.pop();
	    	secondSection = this.sectionsStack.peek();
            	if (!secondSection.sectionId.startsWith("Body"))
	    		title = secondSection.sectionId + "||" + title;
		// update active sections title
	    	activeSection.updateID(title);
	    	// restore stack
	    	this.sectionsStack.push(activeSection);
	    	activeSection = this.sectionsStack.peek();
            }
          } else if ("Section".equals(config.getReadSectionName(localElement))) {
	    //create new section and push it in stack
            Section newSection = createSectionHolder(docId, "Section");
	    this.sectionsStack.push(newSection);
	    this.xmlElmntNamesStack.push(localElement.elementName);
	    //updated activesection to paint to start of stack
	    activeSection = this.sectionsStack.peek();
	    activeXMLElmntName = this.xmlElmntNamesStack.peek();
          } else if ("Xref".equals(config.getDataSectionName(localElement)) && localElement.isBibRef()) {
            activeSection.content.append("<xreffollows>");
          }
          break;
        }
        }
      }
      return true;
    } catch (XMLStreamException ex) {
      System.err.println("Problem with file:" + inputFile.getAbsolutePath());
      ex.printStackTrace();
      return false;
    } 
  }

  private String getFlatElementText(XMLElement element) {
    StringBuilder section = new StringBuilder();
    try {
      loop: for (int e = parser.next(); e != XMLStreamConstants.END_DOCUMENT; e = parser.next()) {
        switch (e) {
        case XMLStreamConstants.CHARACTERS:
          section.append(parser.getText());
          break;

        case XMLStreamConstants.END_ELEMENT: {
          XMLElement localElement = new XMLElement(parser, e);
          if (localElement.elementName.equals(element.elementName)) {
            break loop;
          } else if (config.isSplitSection(localElement.elementName)) {
            if (section.length() > 0 && section.charAt(section.length() - 1) != '.') {
              section.append(".");
            }
            section.append(" ");
          } else if (config.isSplitTag(localElement.elementName)) {
            section.append(" ");
          } else if (config.isMarkdown(localElement.elementName)) {
            section.append(config.getMarkdown(localElement.elementName));
          }
          break;
        }

        case XMLStreamConstants.START_ELEMENT: {
          XMLElement localElement = new XMLElement(parser, e);
          if (config.isSkipSection(localElement.elementName)) {
            skipSection(localElement.elementName);
          } else if (config.isMarkdown(localElement.elementName)) {
            section.append(config.getMarkdown(localElement.elementName));
          }
          break;
        }
        }
      }
      return config.cleanup(section.toString());
    } catch (XMLStreamException ex) {
      ex.printStackTrace();
      return "";
    }
  }

  private Section parseRef(String docId) {
    String title = null;
    String pubId = null;
    String pubYr = null;
    String pubJournal = null;
    try {
      loop: for (int e = parser.next(); e != XMLStreamConstants.END_DOCUMENT; e = parser.next()) {
        switch (e) {
        case XMLStreamConstants.END_ELEMENT: {
          XMLElement localElement = new XMLElement(parser, e);
          if ("Reference".equals(config.getDataSectionName(localElement))) {
            break loop;
          }
          break;
        }
        case XMLStreamConstants.START_ELEMENT: {
          XMLElement localElement = new XMLElement(parser, e);
          if ("Title".equals(config.getHeaderSectionName(localElement))) {
            title = getFlatElementText(localElement);
            if (allTitles.contains(title)) {
              return null;
            }
            allTitles.add(title);
          } else if ("PubId".equals(config.getDataSectionName(localElement))) {
            pubId = getFlatElementText(localElement);
            if (allPubIds.contains(pubId)) {
              return null;
            }
            allPubIds.add(pubId);
            // TODO XXX HACK : This ref format only fits for PMC-OA. If we ever
            // get PubMed citations, we have to change this!!
          } else if ("year".equals(localElement.elementName)) {
            pubYr = getFlatElementText(localElement);
          } else if ("source".equals(localElement.elementName)) {
            pubJournal = getFlatElementText(localElement);
          }
          break;
        }
        }
      }
      if (docId == null) {
        omWriter.println(title);
        return null;
      }
      Metadata refMd = new Metadata();
      refMd.pmid = pubId;
      refMd.journalName = pubJournal;
      refMd.journalYear = pubYr;
      refMd.write(mdWriter);
      return createSection(docId, "Ref", title, pubId);
    } catch (XMLStreamException ex) {
      ex.printStackTrace();
      return null;
    }
  }

  private void parseMetadata(Metadata md) {
    try {
      loop: for (int e = parser.next(); e != XMLStreamConstants.END_DOCUMENT; e = parser.next()) {
        switch (e) {
        case XMLStreamConstants.END_ELEMENT: {
          XMLElement localElement = new XMLElement(parser, e);
          if ("Metadata".equals(config.getDataSectionName(localElement))) {
            break loop;
          }
          break;
        }
        case XMLStreamConstants.START_ELEMENT: {
          XMLElement localElement = new XMLElement(parser, e);
          if ("Journal".equals(config.getDataSectionName(localElement))) {
            md.journalName = getFlatElementText(localElement);
          } else if ("JournalYear".equals(config.getDataSectionName(localElement))) {
            md.journalYear = getFlatElementText(localElement);
          } else if ("ISSNPrint".equals(config.getDataSectionName(localElement))) {
            md.issnPrint = getFlatElementText(localElement);
          } else if ("ISSNElectronic".equals(config.getDataSectionName(localElement))) {
            md.issnElectronic = getFlatElementText(localElement);
          } else if ("ISSNGlobal".equals(config.getDataSectionName(localElement))) {
            md.issnGlobal = getFlatElementText(localElement);
          } else if ("Keyword".equals(config.getDataSectionName(localElement))) {
	    md.keywords.add(getFlatElementText(localElement));
	  } else if ("Heading".equals(config.getDataSectionName(localElement)) && (localElement.attributeValues.contains("heading"))) {
	    md.subject = getFlatElementText(localElement);
	  } else if ("AuthorName".equals(config.getDataSectionName(localElement))) {
	    md.authors.add(getFlatElementText(localElement));
	  }
          break;
        }
        }
      }
    } catch (XMLStreamException ex) {
      ex.printStackTrace();
    }
  }

  private Section createSection(String docId, String sectionId, String text, String refDocId) {
    assert docId != null;
    if (text == null) {
      return null;
    }
    int num;

    // The 'primary key' is always the docId + sectionId
    String pk = docId + "." + sectionId;
    if (seenNames.containsKey(pk)) {
      num = seenNames.get(pk) + 1;
    } else {
      num = 0;
    }
    seenNames.put(pk, num);
    sectionId = sectionId + "." + num;
    Section s = new Section(docId, sectionId, text, refDocId);
    return s;
  }

  private Section createSection(String docId, String sectionId, String text) {
    return createSection(docId, sectionId, text, null);
  }

  private Section createSectionHolder(String docId, String sectionId) {
    assert docId != null;
    int num;

    // The 'primary key' is always the docId + sectionId
    String pk = docId + "." + sectionId;
    if (seenNames.containsKey(pk)) {
      num = seenNames.get(pk) + 1;
    } else {
      num = 0;
    }
    seenNames.put(pk, num);
    sectionId = sectionId + "." + num;
    Section s = new Section(docId, sectionId, null, null);
    return s;
  }

  /**
   * Go through the XML document, pulling out certain flat sections as
   * individual output files.
   */
  public ArrayList<Section> parse() {
    String docId = null;
    Metadata md = null;
    try {
      parser = factory.createXMLStreamReader(this.xmlStream);
      while (true) {
        int event = parser.next();
        if (event == XMLStreamConstants.START_ELEMENT) {
          XMLElement localElement = new XMLElement(parser, event);

          if ("BlockMarker".equals(config.getDataSectionName(localElement))) {
            md = new Metadata();
          }

          // Try to get the doc id
          if (config.isDocIdSection(parser, event)) {
	    if (docId == null) {
            	docId = config.formatDocId(getFlatElementText(localElement));
	    }
            // "Reference" sections not simply in 'scope' because they need
            // special treatment
          } else if ("Reference".equals(config.getDataSectionName(localElement))) {
            Section s = parseRef(docId);
            if (s != null) {
              this.sections.add(s);
            }
          } else if ("Affiliation".equals(config.getDataSectionName(localElement))) {
            md.authorAffs.add(getFlatElementText(localElement)); 
	  }else if ("Metadata".equals(config.getDataSectionName(localElement))) {
            parseMetadata(md);
            md.pmid = docId;

            // get sections that are in scope
            // avoid duplicate titles (due to pulling titles from references
            // section)
          } else if ("MeSH".equals(config.getDataSectionName(localElement))) {
            md.meshTerms.add(getFlatElementText(localElement));
	  } else if ("Body".equals(config.getReadSectionName(localElement))) {
	    skipSection(localElement.elementName);
            if (docId == null) {
              String content = getFlatElementText(localElement);
	      omWriter.println(content);
	    } else {
		// cretae Body section and puth it in the stack
		Section bodySection = createSectionHolder(docId, "Body");
	        sectionsStack.push(bodySection);
            	xmlElmntNamesStack.push(localElement.elementName);
		// parse and extract nested sections
		if (!this.getSectionContent(docId)) {	
			System.err.println("Problem with file:" + inputFile.getAbsolutePath());
		}
            }
          } else if (config.headerSec(localElement)) { 
            String content = getFlatElementText(localElement);
            if (docId == null) {
              omWriter.println(content);
            } else {
              if (config.getHeaderSectionName(localElement).equals("Title")) {
                if (allTitles.contains(content)) {
                  continue;
                }
                allTitles.add(content);
              }
              String sectionName = config.getHeaderSectionName(localElement);
              Section s = createSection(docId, sectionName, content);
              if (s != null) {
                this.sections.add(s);
              }
            }
          }

        } else if (event == XMLStreamConstants.END_ELEMENT) {
          XMLElement localElement = new XMLElement(parser, event);
          if ("BlockMarker".equals(config.getDataSectionName(localElement))) {
            docId = null;
            md.write(mdWriter);
            md = null;
          }

        } else if (event == XMLStreamConstants.END_DOCUMENT) {
          parser.close();
          if (md != null) {
            md.write(mdWriter);
          }
          break;
        }
      }
    } catch (XMLStreamException ex) {
      System.err.println(inputFile.getAbsolutePath());
      ex.printStackTrace();
    }
    return this.sections;
  }

  // Default constructor from InputStream
  public XMLDocParser(File inputFile, XMLDocConfig config, HashSet<String> allTitles, HashSet<String> allPubIds,
      PrintWriter mdWriter, PrintWriter omWriter) throws FileNotFoundException {
    this.inputFile = inputFile;
    this.xmlStream = new FileInputStream(inputFile);
    this.factory = XMLInputFactory.newInstance();
    this.config = config;
    this.allTitles = allTitles;
    this.allPubIds = allPubIds;
    this.mdWriter = mdWriter;
    this.omWriter = omWriter;
  }
}
