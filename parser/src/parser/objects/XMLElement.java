package parser.objects;

import java.util.ArrayList;
import java.util.List;

import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamReader;

public class XMLElement {

  public String elementName;
  public List<String> attributeNames = new ArrayList<>();
  public List<String> attributeValues = new ArrayList<>();

  @Override
  public String toString() {
    return "XMLElement [elementName=" + elementName + ", attributeNames=" + attributeNames + ", attributeValues="
        + attributeValues + "]";
  }

  public XMLElement(XMLStreamReader parser, int xmlStreamConstant) {
    this.elementName = parser.getLocalName();
    if (xmlStreamConstant == XMLStreamConstants.START_ELEMENT) {
      for (int i = 0; i < parser.getAttributeCount(); i++) {
        attributeNames.add(parser.getAttributeLocalName(i));
        attributeValues.add(parser.getAttributeValue(i));
      }
    }
  }

}
