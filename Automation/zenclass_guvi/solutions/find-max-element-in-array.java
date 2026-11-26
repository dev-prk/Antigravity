import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String nLine = br.readLine();
        if (nLine == null || nLine.isEmpty()) {
            return;
        }
        int n = Integer.parseInt(nLine.trim());
        if (n <= 0) {
            return;
        }
        String[] tokens = br.readLine().trim().split("\\s+");
        int max = Integer.MIN_VALUE;
        for (int i = 0; i < n && i < tokens.length; i++) {
            int val = Integer.parseInt(tokens[i]);
            if (val > max) {
                max = val;
            }
        }
        System.out.println(max);
    }
}
