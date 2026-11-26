import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine().trim();
        if (s.startsWith("-")) {
            String rev = new StringBuilder(s.substring(1)).reverse().toString();
            System.out.println("-" + rev);
        } else {
            System.out.println(new StringBuilder(s).reverse().toString());
        }
    }
}
