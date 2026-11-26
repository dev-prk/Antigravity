import java.io.*;
import java.util.*;

public class Main {
    static class FenwickTree {
        private long[] tree;
        private int n;

        public FenwickTree(int size) {
            n = size;
            tree = new long[n + 1];
        }

        public void update(int index, long delta) {
            for (int i = index + 1; i <= n; i += i & (-i)) {
                tree[i] += delta;
            }
        }

        public long prefixSum(int index) {
            long sum = 0;
            for (int i = index + 1; i > 0; i -= i & (-i)) {
                sum += tree[i];
            }
            return sum;
        }

        public long rangeSum(int left, int right) {
            if (left == 0) {
                return prefixSum(right);
            }
            return prefixSum(right) - prefixSum(left - 1);
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int q = Integer.parseInt(st.nextToken());

        int[] arr = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }

        FenwickTree ft = new FenwickTree(n);
        for (int i = 0; i < n; i++) {
            ft.update(i, arr[i]);
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < q; i++) {
            st = new StringTokenizer(br.readLine());
            int type = Integer.parseInt(st.nextToken());

            if (type == 1) {
                int x = Integer.parseInt(st.nextToken());
                int y = Integer.parseInt(st.nextToken());
                long delta = y - arr[x];
                arr[x] = y;
                ft.update(x, delta);
            } else if (type == 2) {
                int l = Integer.parseInt(st.nextToken());
                int r = Integer.parseInt(st.nextToken());
                sb.append(ft.rangeSum(l, r)).append('\n');
            }
        }

        System.out.print(sb.toString());
    }
}
