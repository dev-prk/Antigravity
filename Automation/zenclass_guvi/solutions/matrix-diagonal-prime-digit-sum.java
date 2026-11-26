import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String ns = br.readLine();
        if (ns == null || ns.trim().isEmpty()) {
            System.out.println(0);
            return;
        }
        int n = Integer.parseInt(ns.trim());
        if (n <= 0) {
            System.out.println(0);
            return;
        }
        int[][] mat = new int[n][n];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int j = 0; j < n; j++) {
                if (st.hasMoreTokens()) {
                    mat[i][j] = Integer.parseInt(st.nextToken());
                } else {
                    mat[i][j] = 0;
                }
            }
        }
        Set<Integer> primes = new HashSet<>(Arrays.asList(2, 3, 5, 7));
        int sum = 0;
        for (int i = 0; i < n; i++) {
            int p = mat[i][i];
            if (primes.contains(p)) sum += p;
        }
        for (int i = 0; i < n; i++) {
            int j = n - 1 - i;
            if (j != i) {
                int p = mat[i][j];
                if (primes.contains(p)) sum += p;
            }
        }
        System.out.println(sum);
    }
}
