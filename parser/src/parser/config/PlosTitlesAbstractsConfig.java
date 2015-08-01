package parser.config;

import javax.xml.stream.XMLStreamReader;

public class PlosTitlesAbstractsConfig extends XMLDocConfig {

    public boolean isDocIdSection(XMLStreamReader parser) {
        if (!parser.getLocalName().equals(docIdSection)) {
            return false;
        }
        for (int i = 0; i < parser.getAttributeCount(); i++) {
            if (parser.getAttributeValue(i).equals("doi")) {
                return true;
            }
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
        readSections.put("article-title", "Title");
        readSections.put("abstract", "Abstract");
        dataSections.put("ref", "Reference");
        dataSections.put("pub-id", "PubId");

        String[] skipSections = { "title", "xref", "table-wrap", "table", "object-id", "label", "caption", "ext-link" };
        addSkipSections(skipSections);

        String[] splitSections = { "p", "div", "li", "ref" };
        addSplitSections(splitSections);

        String[] splitTags = { "surname" };
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

    // currently unused here
    public boolean isStartBlock(String localName) {
        return false;
    }

    public boolean isEndBlock(String localName) {
        return false;
    }

}
