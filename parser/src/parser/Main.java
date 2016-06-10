package parser;

import java.io.File;
import java.io.FileWriter;
import java.io.BufferedWriter;
import java.io.PrintWriter;
import java.io.IOException;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.HashSet;

import org.json.simple.JSONObject;

import parser.config.XMLDocConfig;
import parser.config.PlosConfig;
import parser.config.PubmedTitlesAbstractsConfig;
import parser.objects.Section;

public class Main {

  // XXX Might cause memory trouble in the future on large datasets
  public static HashSet<String> allTitles = new HashSet<String>();
  public static HashSet<String> allPubIds = new HashSet<String>();

  @SuppressWarnings("unchecked")
  public static void main(String[] args) {
    if (args.length != 4) {
      System.out.println("Usage: java -ea -jar parser.jar [input-type] [input-file-or-dir] [metadata-file] [omitted-file]");
      System.exit(0);
    }
    ArrayList<File> files = getAllFiles(args[1]);
    File mdFile = new File(args[2]);
    File omFile = new File(args[3]);
    PrintWriter mdWriter = null;
    PrintWriter omWriter = null;
    if (mdFile != null) {
      try {
        mdWriter = new PrintWriter(new BufferedWriter(new FileWriter(mdFile)));
      } catch (FileNotFoundException e) {
        e.printStackTrace();
      } catch (IOException e) {
        e.printStackTrace();
      }
    }
    if (omFile != null) {
      try {
        omWriter = new PrintWriter(new BufferedWriter(new FileWriter(omFile)));
      } catch (FileNotFoundException e) {
        e.printStackTrace();
      } catch (IOException e) {
        e.printStackTrace();
      }
    }

    // Set XMLDocConfig dynamically
    XMLDocConfig config = null;
    if (args[0].equals("plos") || args[0].equals("pmc")) {
      config = new PlosConfig();
    } else if (args[0].equals("pubmed")) {
      config = new PubmedTitlesAbstractsConfig();
    }

    try {
      for (File file : files) {
	System.err.println("Processing file:" + file.getAbsolutePath());
        XMLDocParser docParser = new XMLDocParser(file, config, allTitles, allPubIds, mdWriter, omWriter);
        for (Section s : docParser.parse()) {
          JSONObject obj = new JSONObject();
          obj.put("doc-id", s.docId);
          obj.put("section-id", s.sectionId);
          obj.put("ref-doc-id", s.refDocId);
          obj.put("content", s.sectionText);
          System.out.println(obj.toJSONString());
        }
      }
    } catch (Throwable err) {
      err.printStackTrace();
      System.exit(0);
    }
    mdWriter.close();
    omWriter.close();
  }

  public static void addAllFiles(ArrayList<File> files, File file) {
    if (file.isFile()) {
      files.add(file);
    } else if (file.isDirectory()) {
      for (File f : file.listFiles()) {
        addAllFiles(files, f);
      }
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
