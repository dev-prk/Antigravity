import java.io.*;
import java.util.*;

public class Main {
    static class SegmentTree {
        long[] tree;
        long[] lazy;
        long[] arr;
        int n;

        public SegmentTree(long[] arr) {
            this.arr = arr;
            this.n = arr.length;
            tree = new long[4 * n];
            lazy = new long[4 * n];
            Arrays.fill(lazy, 0);
            build(1, 0, n - 1);
        }

        private void build(int node, int start, int end) {
            if (start == end) {
                tree[node] = (arr[start] % 2 == 0) ? arr[start] : 0;
            } else {
                int mid = (start + end) / 2;
                build(2 * node, start, mid);
                build(2 * node + 1, mid + 1, end);
                tree[node] = tree[2 * node] + tree[2 * node + 1];
            }
            lazy[node] = 0;
        }

        private void push(int node, int start, int end) {
            if (lazy[node] != 0) {
                tree[node] += lazy[node] * (end - start + 1);
                if (start != end) {
                    lazy[2 * node] += lazy[node];
                    lazy[2 * node + 1] += lazy[node];
                }
                lazy[node] = 0;
            }
        }

        public long query(int l, int r) {
            return query(1, 0, n - 1, l - 1, r - 1);
        }

        private long query(int node, int start, int end, int l, int r) {
            push(node, start, end);
            if (r < start || end < l) return 0;
            if (l <= start && end <= r) return tree[node];
            int mid = (start + end) / 2;
            return query(2 * node, start, mid, l, r) +
                   query(2 * node + 1, mid + 1, end, l, r);
        }

        public void update(int idx, long newVal) {
            update(1, 0, n - 1, idx - 1, newVal);
        }

        private void update(int node, int start, int end, int idx, long newVal) {
            if (start == end) {
                arr[start] = newVal;
                tree[node] = (newVal % 2 == 0) ? newVal : 0;
                return;
            }
            int mid = (start + end) / 2;
            if (idx <= mid) {
                update(2 * node, start, mid, idx, newVal);
            } else {
                update(2 * node + 1, mid + 1, end, idx, newVal);
            }
            tree[node] = tree[2 * node] + tree[2 * node + 1];
        }
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().split("\\s+");
        int n = Integer.parseInt(parts[0]);
        int q = Integer.parseInt(parts[1]);
        long[] arr = new long[n];
        parts = br.readLine().split("\\s+");
        for (int i = 0; i < n; i++) {
            arr[i] = Long.parseLong(parts[i]);
        }
        SegmentTree st = new SegmentTree(arr);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < q; i++) {
            parts = br.readLine().split("\\s+");
            int type = Integer.parseInt(parts[0]);
            if (type == 1) {
                int x = Integer.parseInt(parts[1]);
                long y = Long.parseLong(parts[2]);
                st.update(x, y);
            } else {
                int l = Integer.parseInt(parts[1]);
                int r = Integer.parseInt(parts[2]);
                sb.append(st.query(l, r)).append("\n");
            }
        }
        System.out.print(sb.toString());
    }
}
