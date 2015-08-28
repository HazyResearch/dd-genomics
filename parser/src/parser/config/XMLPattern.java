package parser.config;

public class XMLPattern {

  public String elementName;
  
  // extend this to list, make getters and setters whenever you feel
  // you have too much time on your hands.
  // I currently need one elementName and one attributeName
  public String attributeName;
  public String attributeValue;
  
  public XMLPattern(String elementName, String attributeName, String attributeValue) {
    this.elementName = elementName;
    this.attributeName = attributeName;
    this.attributeValue = attributeValue;
  }
  
  public XMLPattern(String elementName) {
    this(elementName, null, null);
  }
  
}
