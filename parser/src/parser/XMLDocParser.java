package parser;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;

import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamReader;

import parser.config.XMLDocConfig;
import parser.metadata.Metadata;
import parser.objects.OutputDoc;

public class XMLDocParser {
	private InputStream xmlStream;
	private XMLInputFactory factory;
	private XMLStreamReader parser;
	private XMLDocConfig config;
	private HashSet<String> allTitles;
	private HashSet<String> allPubIds;
	private HashMap<String, Integer> seenNames = new HashMap<String, Integer>();
	private PrintWriter mdWriter;

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
						if (section.length() > 0 && section.charAt(section.length() - 1) != '.') {
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

	private String parseRef() {
		String title = null;
		try {
			loop: for (int e = parser.next(); e != XMLStreamConstants.END_DOCUMENT; e = parser.next()) {
				switch (e) {
				case XMLStreamConstants.END_ELEMENT: {
					String localName = parser.getLocalName();
					if ("Reference".equals(config.getDataSectionName(localName))) {
						break loop;
					}
					break;
				}
				case XMLStreamConstants.START_ELEMENT: {
					String localName = parser.getLocalName();
					if ("Title".equals(config.getReadSectionName(localName))) {
						title = getFlatElementText(localName);
					} else if ("PubId".equals(config.getDataSectionName(localName))) {
						String pubId = getFlatElementText(localName);
						if (allPubIds.contains(pubId))
							return null;
						allPubIds.add(pubId);
					}
					break;
				}
				}
			}
			return title;
		} catch (XMLStreamException ex) {
			System.out.println(ex);
			return null;
		}
	}

	private Metadata parseMetadata() {
		Metadata md = new Metadata();
		try {
			loop: for (int e = parser.next(); e != XMLStreamConstants.END_DOCUMENT; e = parser.next()) {
				switch (e) {
				case XMLStreamConstants.END_ELEMENT: {
					String localName = parser.getLocalName();
					if ("Metadata".equals(config.getDataSectionName(localName))) {
						break loop;
					}
					break;
				}
				case XMLStreamConstants.START_ELEMENT: {
					String localName = parser.getLocalName();
					if ("Journal".equals(config.getDataSectionName(localName))) {
						md.journalName = getFlatElementText(localName);
					} else if ("JournalYear".equals(config.getDataSectionName(localName))) {
						md.journalYear = getFlatElementText(localName);
					}
					break;
				}
				}
			}
			return md;
		} catch (XMLStreamException ex) {
			System.out.println(ex);
			return null;
		}
	}

	private OutputDoc createOutDoc(String docId, String content, String sectionName) {
		assert docId != null;
		int num;
		String docName = docId + "." + sectionName;
		if (seenNames.containsKey(docName)) {
			num = seenNames.get(docName) + 1;
		} else {
			num = 0;
		}
		seenNames.put(docName, num);
		docName = docName + "." + num;
		OutputDoc outDoc = new OutputDoc(docName, content);
		return outDoc;
	}

	/**
	 * Go through the XML document, pulling out certain flat sections as
	 * individual output files.
	 */
	public ArrayList<OutputDoc> parse() {
		String docId = null;
		Metadata md = null;
		ArrayList<OutputDoc> outDocs = new ArrayList<OutputDoc>();
		try {
			parser = factory.createXMLStreamReader(this.xmlStream);
			while (true) {
				int event = parser.next();
				if (event == XMLStreamConstants.START_ELEMENT) {
					String localName = parser.getLocalName();
					// Try to get the doc id
					if (config.isDocIdSection(parser)) {
						docId = config.formatDocId(getFlatElementText(localName));
						md = new Metadata();
					} else if ("BlockMarker".equals(config.getDataSectionName(localName))) {
						assert docId == null : docId + ", " + localName;
						assert md == null;
					} else if ("Reference".equals(config.getDataSectionName(localName))) {
						// "Reference" sections not simply in 'scope' because
						// they need special treatment
						String refTitle = parseRef();
						if (refTitle == null)
							continue;
						if (allTitles.contains(refTitle)) {
							continue;
						}
						allTitles.add(refTitle);
						OutputDoc outDoc = createOutDoc(docId, refTitle, "Title");
						md.id = outDoc.docName;
						md.write(mdWriter);
						outDocs.add(outDoc);
					} else if ("Metadata".equals(config.getDataSectionName(localName))) {
						md = parseMetadata();
						md.pmid = docId;
					} else if (config.readable(localName)) {
						// get sections that are in scope
						assert docId != null;
						// avoid duplicate titles (due to pulling titles from
						// references section)
						String content = getFlatElementText(localName);
						if (config.getReadSectionName(localName).equals("Title")) {
							if (allTitles.contains(content))
								continue;
							allTitles.add(content);
						}
						OutputDoc outDoc = createOutDoc(docId, content, config.getReadSectionName(localName));
						md.id = outDoc.docName;
						md.write(mdWriter);
						outDocs.add(outDoc);
					}
				} else if (event == XMLStreamConstants.END_ELEMENT) {
					String localName = parser.getLocalName();
					if ("BlockMarker".equals(config.getDataSectionName(localName))) {
						docId = null;
						md = null;
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

	// Default constructor from InputStream
	public XMLDocParser(InputStream xmlStream, XMLDocConfig config, HashSet<String> allTitles,
			HashSet<String> allPubIds, File mdFile) {
		this.xmlStream = xmlStream;
		this.factory = XMLInputFactory.newInstance();
		this.config = config;
		this.allTitles = allTitles;
		this.allPubIds = allPubIds;
		if (mdFile != null) {
			try {
				mdWriter = new PrintWriter(mdFile);
			} catch (FileNotFoundException e) {
				e.printStackTrace();
			}
		}
	}

	@Override
	public void finalize() {
		if (mdWriter != null) {
			mdWriter.close();
		}
	}

}
