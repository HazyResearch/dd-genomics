package parser.config;

import javax.xml.stream.XMLStreamReader;

public class PubmedTitlesAbstractsConfig extends XMLDocConfig {

	public boolean isDocIdSection(XMLStreamReader parser) {
		if (!parser.getLocalName().equals(docIdSection)) {
			return false;
		}
		return true;
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
		readSections.put("ArticleTitle", "Title");
		readSections.put("AbstractText", "Abstract");
		dataSections.put("Journal", "Metadata"); // that's right --- the
													// metadata section is
													// called "Journal" in
													// pubmed files
		dataSections.put("ISOAbbreviation", "Journal");
		dataSections.put("Year", "JournalYear");
		dataSections.put("MedlineCitation", "BlockMarker");

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
