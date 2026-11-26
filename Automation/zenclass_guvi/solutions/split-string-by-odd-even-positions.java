import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null || s.length() == 0) {
            System.out.println(" ");
            return;
        }
        s = s.trim();
        StringBuilder odd = new StringBuilder();
        StringBuilder even = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            if ((i + 1) % 2 == 1) {
                odd.append(s.charAt(i));
            } else {
                even.append(s.charAt(i));
            }
        }
        System.out.println(odd.toString() + " " + even.toString());
    }
}
