import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null) return;
        line = line.trim();
        if (line.isEmpty()) return;
        int n = Integer.parseInt(line);
        
        List<String> words = new ArrayList<>();
        while (words.size() < n) {
            line = br.readLine();
            if (line == null) break;
            line = line.trim();
            if (line.isEmpty()) continue;
            String[] parts = line.split("\\s+");
            for (String p : parts) {
                if (words.size() >= n) break;
                words.add(p);
            }
        }
        
        int maxLen = 0;
        for (String w : words) {
            if (w.length() > maxLen) maxLen = w.length();
        }
        
        StringBuilder sb = new StringBuilder();
        for (String w : words) {
            if (w.length() == maxLen) {
                sb.append(w).append("\n");
            }
        }
        System.out.print(sb.toString());
    }
}
