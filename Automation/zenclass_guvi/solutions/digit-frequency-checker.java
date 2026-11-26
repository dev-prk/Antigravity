import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine().trim();
        int[] freq = new int[10];
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (Character.isDigit(c)) {
                freq[c - '0']++;
            }
        }
        for (int i = 0; i < 10; i++) {
            if (freq[i] > 0) {
                System.out.println(i + " " + freq[i]);
            }
        }
    }
}
