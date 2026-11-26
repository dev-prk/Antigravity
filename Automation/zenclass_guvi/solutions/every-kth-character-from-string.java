import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null || line.isEmpty()) {
            return;
        }
        
        line = line.trim();
        int lastSpace = line.lastIndexOf(' ');
        if (lastSpace == -1) {
            return;
        }
        
        String s = line.substring(0, lastSpace);
        int k = Integer.parseInt(line.substring(lastSpace + 1).trim());
        
        StringBuilder sb = new StringBuilder();
        for (int i = k - 1; i < s.length(); i += k) {
            if (sb.length() > 0) sb.append(' ');
            sb.append(s.charAt(i));
        }
        
        System.out.print(sb.toString());
    }
}
