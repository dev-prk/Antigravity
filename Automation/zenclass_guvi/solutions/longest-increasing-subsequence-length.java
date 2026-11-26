import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String nStr = br.readLine();
        if (nStr == null || nStr.trim().isEmpty()) {
            System.out.println(0);
            return;
        }
        int n = Integer.parseInt(nStr.trim());
        if (n == 0) {
            System.out.println(0);
            return;
        }
        String line = br.readLine();
        if (line == null || line.trim().isEmpty()) {
            System.out.println(0);
            return;
        }
        line = line.trim();
        if (line.isEmpty()) {
            System.out.println(0);
            return;
        }
        String[] parts = line.split("\\s+");
        int[] arr = new int[n];
        for (int i = 0; i < n && i < parts.length; i++) {
            arr[i] = Integer.parseInt(parts[i]);
        }
        int[] tails = new int[n];
        int len = 0;
        for (int i = 0; i < n; i++) {
            int x = arr[i];
            int lo = 0, hi = len;
            while (lo < hi) {
                int mid = (lo + hi) / 2;
                if (tails[mid] < x) {
                    lo = mid + 1;
                } else {
                    hi = mid;
                }
            }
            tails[lo] = x;
            if (lo == len) {
                len++;
            }
        }
        System.out.println(len);
    }
}
