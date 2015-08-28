package parser.objects;

import java.io.PrintWriter;

public class Metadata {
  public String pmid;
  public String journalName;
  public String journalYear;
  public String issnGlobal;
  public String issnPrint;
  public String issnElectronic;

  @Override
  public String toString() {
    return pmid + "\t" + journalName + "\t" + journalYear + "\t" + issnGlobal + "\t" + issnPrint + "\t" + issnElectronic;
  }

  public boolean isEmpty() {
    return pmid == null && journalName == null;
  }

  public void write(PrintWriter mdWriter) {
    if (mdWriter != null) {
      if (!isEmpty()) { mdWriter.println(this); }
    }
  }
}
