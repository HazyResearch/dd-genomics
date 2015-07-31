package parser;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashSet;

import org.json.simple.JSONObject;

import parser.config.PubmedTitlesAbstractsConfig;
import parser.config.XMLDocConfig;
import parser.objects.OutputDoc;

public class MainPubmed {

	// XXX Might cause memory trouble in the future on large datasets
	public static HashSet<String> allTitles = new HashSet<String>();
	public static HashSet<String> allPubIds = new HashSet<String>();

	@SuppressWarnings("unchecked")
	public static void main(String[] args) {
		if (args.length != 2) {
			System.out.println("Usage: java -ea -jar parser-titles-abstracts.jar input-file-or-dir metadata-file");
			System.exit(0);
		}

		ArrayList<File> files = getAllFiles(args[0]);
		File metadataFile = new File(args[1]);

		XMLDocConfig config = new PubmedTitlesAbstractsConfig();

		try {
			for (File file : files) {
				InputStream xmlInput = new FileInputStream(file);
				XMLDocParser docParser = new XMLDocParser(xmlInput, config, allTitles, allPubIds, metadataFile);

				// TODO: make this actually streaming? I.e. call a
				// docParser.getNext() method
				for (OutputDoc outDoc : docParser.parse()) {
					// JSON
					JSONObject obj = new JSONObject();
					obj.put("item_id", outDoc.docName);
					obj.put("content", outDoc.docText);
					System.out.println(obj.toJSONString());
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
