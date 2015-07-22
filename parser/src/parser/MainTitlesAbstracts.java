package parser;

import parser.config.*;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.FileInputStream;
import java.util.ArrayList;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

public class MainTitlesAbstracts {

  public static void main(String[] args) {
    if (args.length != 1) {
      System.out.println("Usage: java -ea -jar parser-titles-abstracts.jar [FILE OR DIR]");
      System.exit(0);
    }

    ArrayList<File> files = getAllFiles(args[0]);

    XMLDocConfig config = new PlosTitlesAbstractsConfig();

    try {
      for (File file : files) {
        InputStream xmlInput = new FileInputStream(file);
        XMLDocParser docParser = new XMLDocParser(xmlInput, config);

        // TODO: make this actually streaming?  I.e. call a docParser.getNext() method
        for (OutputDoc outDoc : docParser.parse()) {

          // JSON
          JSONObject obj = new JSONObject();
          obj.put("item_id", outDoc.docName);
          obj.put("content", outDoc.docText);
          System.out.println(obj.toJSONString());

          // TSV
          /*
          System.out.print(outDoc.docName);
          System.out.print("\t");
          System.out.print(outDoc.docText);
          System.out.print("\n");
          */
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
