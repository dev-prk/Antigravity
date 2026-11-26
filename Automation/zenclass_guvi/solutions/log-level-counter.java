import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        
        if (line == null) {
            System.out.println("ERROR: 0");
            System.out.println("INFO: 0");
            System.out.println("WARNING: 0");
            return;
        }
        
        int n = Integer.parseInt(line.trim());
        
        int errorCount = 0;
        int infoCount = 0;
        int warningCount = 0;
        
        for (int i = 0; i < n; i++) {
            String logEntry = br.readLine();
            if (logEntry == null) break;
            
            if (logEntry.contains("ERROR")) {
                errorCount++;
            } else if (logEntry.contains("INFO")) {
                infoCount++;
            } else if (logEntry.contains("WARNING")) {
                warningCount++;
            }
        }
        
        System.out.println("ERROR: " + errorCount);
        System.out.println("INFO: " + infoCount);
        System.out.println("WARNING: " + warningCount);
    }
}
