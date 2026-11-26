import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String nLine = br.readLine();
        if (nLine == null || nLine.isEmpty()) {
            return;
        }
        int n = Integer.parseInt(nLine.trim());
        if (n <= 0) {
            return;
        }
        String line = br.readLine();
        if (line == null) {
            return;
        }
        String[] parts = line.trim().split("\\s+");
        int min = Integer.MAX_VALUE;
        for (int i = 0; i < n && i < parts.length; i++) {
            int val = Integer.parseInt(parts[i].trim());
            if (val < min) {
                min = val;
            }
        }
        System.out.println(min);
    }
}
