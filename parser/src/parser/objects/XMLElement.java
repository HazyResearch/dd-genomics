package parser.objects;

import java.util.ArrayList;
import java.util.List;

import javax.xml.stream.XMLStreamReader;

public class XMLElement {

  public String elementName;
  public List<String> attributeNames = new ArrayList<>();
  public List<String> attributeValues = new ArrayList<>();
  
  public XMLElement(XMLStreamReader parser) {
    this.elementName = parser.getLocalName();
    for (int i = 0; i < parser.getAttributeCount(); i++) {
      attributeNames.add(parser.getAttributeLocalName(i));
      attributeValues.add(parser.getAttributeValue(i));
    }
  }
  
}
