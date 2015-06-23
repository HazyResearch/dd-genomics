package parser;

import parser.config.*;

import java.io.File;
import java.io.InputStream;
import java.io.FileInputStream;
import java.util.ArrayList;

public class Main {

  public static void main(String[] args) {
    if (args.length != 1) {
      System.out.println("Usage: java -ea -jar parser.jar [FILE OR DIR]");
      System.exit(0);
    }
    ArrayList<File> files = getAllFiles(args[0]);

    XMLDocConfig config = new PlosConfig();

    try {
      for (File file : files) {
        InputStream xmlInput = new FileInputStream(file);
        XMLDocParser docParser = new XMLDocParser(xmlInput, config);
        ArrayList<OutputDoc> outDocs = docParser.parse();
        for (OutputDoc outDoc : outDocs) {
          System.out.print(outDoc.docName);
          System.out.print("\t");
          System.out.print(outDoc.docText);
          System.out.print("\n");
        }
      }
    } catch (Throwable err) {
      err.printStackTrace();
      System.exit(0);
    }
  }

  public static void addAllFiles(ArrayList<File> files, File file) {
    if (file.isFile()) {
      files.add(file);
    } else if (file.isDirectory()) {
      for (File f : file.listFiles()) { addAllFiles(files, f); }
    }
  }

  public static ArrayList<File> getAllFiles(String path) {
    ArrayList<File> files = new ArrayList<File>();
    File file = new File(path);
    assert file.exists();
    addAllFiles(files, file);
    return files;
  }
}
