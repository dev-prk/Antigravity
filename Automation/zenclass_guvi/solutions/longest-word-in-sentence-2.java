import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        
        if (s == null || s.isEmpty()) {
            System.out.println("");
            return;
        }
        
        String[] words = s.trim().split("\\s+");
        
        if (words.length == 0 || (words.length == 1 && words[0].isEmpty())) {
            System.out.println("");
            return;
        }
        
        String longest = "";
        for (String word : words) {
            if (!word.isEmpty() && word.length() > longest.length()) {
                longest = word;
            }
        }
        
        System.out.println(longest);
    }
}
