import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        
        if (line == null) {
            System.out.println("no");
            return;
        }
        
        int firstSpace = -1;
        int len = line.length();
        for (int i = 0; i < len; i++) {
            if (line.charAt(i) == ' ') {
                firstSpace = i;
                break;
            }
        }
        
        String s1, s2;
        if (firstSpace == -1) {
            s1 = line;
            s2 = "";
        } else {
            s1 = line.substring(0, firstSpace);
            int secondSpace = -1;
            for (int i = firstSpace + 1; i < len; i++) {
                if (line.charAt(i) == ' ') {
                    secondSpace = i;
                    break;
                }
            }
            if (secondSpace == -1) {
                s2 = line.substring(firstSpace + 1);
            } else {
                s2 = line.substring(firstSpace + 1, secondSpace);
            }
        }
        
        if (s1.length() != s2.length()) {
            System.out.println("no");
            return;
        }
        
        boolean equal = true;
        for (int i = 0; i < s1.length(); i++) {
            if (s1.charAt(i) != s2.charAt(i)) {
                equal = false;
                break;
            }
        }
        
        System.out.println(equal ? "yes" : "no");
    }
}
