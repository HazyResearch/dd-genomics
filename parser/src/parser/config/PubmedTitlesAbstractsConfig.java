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
        readSections.put(new XMLPattern("ArticleTitle"), "Title");
        readSections.put(new XMLPattern("AbstractText"), "Abstract");
        dataSections.put(new XMLPattern("Journal"), "Metadata"); // that's right --- the
                                                 // metadata section is
                                                 // called "Journal" in
                                                 // pubmed files
        dataSections.put(new XMLPattern("ISOAbbreviation"), "Journal");
        dataSections.put(new XMLPattern("Year"), "JournalYear");
        dataSections.put(new XMLPattern("MedlineCitation"), "BlockMarker");
        dataSections.put(new XMLPattern("ISSNLinking"), "ISSNGlobal");
        dataSections.put(new XMLPattern("NlmUniqueID"), "NlmID");
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
