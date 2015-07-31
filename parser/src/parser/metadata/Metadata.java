
package parser.metadata;

import java.io.PrintWriter;

public class Metadata {

	public String id;
	public String pmid;
	public String journalName;
	public String journalYear;

	@Override
	public String toString() {
		return id + "\t" + pmid + "\t" + journalName + "\t" + journalYear;
	}

	public boolean isEmpty() {
		return id == null && pmid == null && journalName == null && journalYear == null;
	}

	public void write(PrintWriter mdWriter) {
		if (mdWriter != null) {
			if (!isEmpty())
				mdWriter.println(this);
		}
	}

}
