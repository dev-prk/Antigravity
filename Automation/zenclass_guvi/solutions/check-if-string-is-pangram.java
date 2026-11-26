import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        
        if (s == null) {
            System.out.println("NO");
            return;
        }
        
        boolean[] seen = new boolean[26];
        int count = 0;
        
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c >= 'A' && c <= 'Z') {
                int idx = c - 'A';
                if (!seen[idx]) {
                    seen[idx] = true;
                    count++;
                }
            } else if (c >= 'a' && c <= 'z') {
                int idx = c - 'a';
                if (!seen[idx]) {
                    seen[idx] = true;
                    count++;
                }
            }
        }
        
        if (count == 26) {
            System.out.println("YES");
        } else {
            System.out.println("NO");
        }
    }
}
