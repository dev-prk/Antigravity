import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String nLine = br.readLine();
        if (nLine == null || nLine.isEmpty()) {
            System.out.println(0);
            return;
        }
        int n = Integer.parseInt(nLine.trim());
        if (n <= 0) {
            System.out.println(0);
            return;
        }
        String line = br.readLine();
        if (line == null || line.isEmpty()) {
            System.out.println(0);
            return;
        }
        String[] parts = line.trim().split("\\s+");
        long sum = 0;
        for (int i = 0; i < parts.length && i < n; i++) {
            int val = Integer.parseInt(parts[i]);
            if (i % 2 == 1) {
                sum += val;
            }
        }
        System.out.println(sum);
    }
}
