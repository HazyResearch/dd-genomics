package parser;

import parser.config.*;

import java.io.InputStream;
import java.io.FileInputStream;
import java.util.ArrayList;

public class Main {
  public static void main(String[] args) {

    String SAMPLEDOC = "sample_data/plos/PLoS_One_2013_Jun_19_8(6)_e66312.nxml";

    XMLDocConfig config = new PlosConfig();

    try {
      InputStream xmlInput = new FileInputStream(SAMPLEDOC);
      XMLDocParser docParser = new XMLDocParser(xmlInput, config);
      ArrayList<OutputDoc> outDocs = docParser.parse();
      for (OutputDoc outDoc : outDocs) {
        System.out.print(outDoc.docName);
        System.out.print("\t");
        System.out.print(outDoc.docText);
        System.out.print("\n");
      }
    } catch (Throwable err) {
      err.printStackTrace();
      System.exit(0);
    }
  }
}
