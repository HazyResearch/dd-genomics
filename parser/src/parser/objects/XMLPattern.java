package parser.objects;

import java.util.ArrayList;
import java.util.List;

public class XMLPattern {

  public String elementName;

  public List<String> attributeNames = new ArrayList<>();
  public List<String> attributeValues = new ArrayList<>();

  private boolean checkAttributes;

  public XMLPattern(String elementName, String attributeName, String attributeValue) {
    this.elementName = elementName;
    this.attributeNames.add(attributeName);
    this.attributeValues.add(attributeValue);
  }

  public XMLPattern(String elementName, boolean checkAttributes) {
    this.elementName = elementName;
    this.checkAttributes = checkAttributes;
  }

  public boolean matches(XMLElement e) {
    if (!elementName.equals(e.elementName))
      return false;
    if (!checkAttributes)
      return true;
    for (int i = 0; i < attributeNames.size(); i++) {
      String an = attributeNames.get(i);
      String av = attributeValues.get(i);
      int index;
      if ((index = e.attributeNames.indexOf(an)) != -1) {
        if (av != null)
          if (!e.attributeValues.get(index).equals(av))
            return false;
      } else {
        return false;
      }
    }
    return true;
  }

  @Override
  public String toString() {
    return "XMLPattern [elementName=" + elementName + ", attributeNames=" + attributeNames + ", attributeValues="
        + attributeValues + "]";
  }

}
