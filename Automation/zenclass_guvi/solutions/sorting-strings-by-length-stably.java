import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null) return;
        int n = Integer.parseInt(s.trim());
        if (n <= 0) return;
        String[] arr = new String[n];
        for (int i = 0; i < n; i++) {
            arr[i] = br.readLine();
        }
        Integer[] idx = new Integer[n];
        for (int i = 0; i < n; i++) idx[i] = i;
        Arrays.sort(idx, (a, b) -> {
            int lenA = arr[a].length();
            int lenB = arr[b].length();
            if (lenA != lenB) return Integer.compare(lenA, lenB);
            return Integer.compare(a, b);
        });
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            sb.append(arr[idx[i]]).append('\n');
        }
        System.out.print(sb.toString());
    }
}
