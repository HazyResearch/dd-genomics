package parser.objects;

import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

public class Metadata {
  public String pmid;
  public String journalName;
  public String journalYear;
  public String issnGlobal;
  public String issnPrint;
  public String issnElectronic;
  public String subject;
  public ArrayList<String> authorAffs = new ArrayList<String>();
  public ArrayList<String> authors = new ArrayList<String>();
  public ArrayList<String> keywords = new ArrayList<String>();
  public List<String> meshTerms = new ArrayList<String>();

  @Override
  public String toString() {
    return pmid + "\t" + journalName + "\t" + journalYear 
	+ "\t" + String.join("|^|", keywords) 
	+ "\t" + String.join("|^|", authorAffs)
	+ "\t" + String.join("|^|", authors)
	+ "\t" + subject
	+ "\t" + issnGlobal 
        + "\t" + issnPrint + "\t" + issnElectronic + "\t" 
        + String.join("|^|", meshTerms);
  }

  public boolean isEmpty() {
    return pmid == null && journalName == null;
  }

  public void write(PrintWriter mdWriter) {
    if (mdWriter != null) {
      if (!isEmpty()) {
        mdWriter.println(this);
      }
    }
  }
}
