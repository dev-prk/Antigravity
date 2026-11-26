import java.io.*;
import java.util.*;

public class Main {
    static class FenwickTree {
        private int[] tree;
        private int n;

        public FenwickTree(int size) {
            this.n = size;
            this.tree = new int[n + 1];
        }

        public void update(int idx, int delta) {
            for (int i = idx; i <= n; i += i & (-i)) {
                tree[i] += delta;
            }
        }

        public int query(int idx) {
            int sum = 0;
            for (int i = idx; i > 0; i -= i & (-i)) {
                sum += tree[i];
            }
            return sum;
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String nStr = br.readLine();
        if (nStr == null || nStr.trim().isEmpty()) {
            System.out.println(0);
            return;
        }
        int n = Integer.parseInt(nStr.trim());
        if (n <= 0) {
            System.out.println(0);
            return;
        }

        String[] parts = br.readLine().trim().split("\\s+");
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(parts[i]);
        }

        // Coordinate compression
        int[] sorted = arr.clone();
        Arrays.sort(sorted);
        Map<Integer, Integer> rankMap = new HashMap<>();
        int rank = 1;
        for (int val : sorted) {
            if (!rankMap.containsKey(val)) {
                rankMap.put(val, rank++);
            }
        }

        FenwickTree ft = new FenwickTree(rank);
        long inversions = 0;

        // Count inversions from right to left
        for (int i = n - 1; i >= 0; i--) {
            int r = rankMap.get(arr[i]);
            inversions += ft.query(r - 1);
            ft.update(r, 1);
        }

        System.out.println(inversions);
    }
}
