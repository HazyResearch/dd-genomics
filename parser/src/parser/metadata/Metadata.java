
package parser.metadata;

public class Metadata {

  public String pmid;
  public String journalName;
  public String journalYear;

  @Override
  public String toString() {
    return pmid + "\t" + journalName + "\t" + journalYear;
  }

}
