import java.io.*;
import java.util.*;

public class Main {
    static class SegmentTree {
        long[] tree;
        long[] lazy;
        int n;
        int k;

        public SegmentTree(int[] arr, int power) {
            this.n = arr.length;
            this.k = power;
            this.tree = new long[4 * n];
            this.lazy = new long[4 * n];
            build(arr, 1, 0, n - 1);
        }

        private void build(int[] arr, int node, int start, int end) {
            if (start == end) {
                tree[node] = pow(arr[start], k);
                lazy[node] = 0;
            } else {
                int mid = (start + end) / 2;
                build(arr, 2 * node, start, mid);
                build(arr, 2 * node + 1, mid + 1, end);
                tree[node] = tree[2 * node] + tree[2 * node + 1];
                lazy[node] = 0;
            }
        }

        private long pow(long base, int exp) {
            long result = 1;
            for (int i = 0; i < exp; i++) {
                result *= base;
            }
            return result;
        }

        public void update(int idx, long val) {
            updateUtil(1, 0, n - 1, idx, val);
        }

        private void updateUtil(int node, int start, int end, int idx, long val) {
            if (lazy[node] != 0) {
                tree[node] = propagate(start, end, lazy[node]);
                if (start != end) {
                    lazy[2 * node] = lazy[node];
                    lazy[2 * node + 1] = lazy[node];
                }
                lazy[node] = 0;
            }

            if (start == end) {
                tree[node] = pow(val, k);
                return;
            }

            int mid = (start + end) / 2;
            if (idx <= mid) {
                updateUtil(2 * node, start, mid, idx, val);
            } else {
                updateUtil(2 * node + 1, mid + 1, end, idx, val);
            }
            tree[node] = tree[2 * node] + tree[2 * node + 1];
        }

        private long propagate(int start, int end, long delta) {
            long sum = 0;
            for (int i = start; i <= end; i++) {
                sum += pow(delta, k);
            }
            return sum;
        }

        public long query(int l, int r) {
            return queryUtil(1, 0, n - 1, l, r);
        }

        private long queryUtil(int node, int start, int end, int l, int r) {
            if (r < start || l > end) {
                return 0;
            }

            if (l <= start && end <= r) {
                return tree[node];
            }

            if (lazy[node] != 0) {
                tree[node] = propagate(start, end, lazy[node]);
                if (start != end) {
                    lazy[2 * node] = lazy[node];
                    lazy[2 * node + 1] = lazy[node];
                }
                lazy[node] = 0;
            }

            int mid = (start + end) / 2;
            long leftSum = queryUtil(2 * node, start, mid, l, r);
            long rightSum = queryUtil(2 * node + 1, mid + 1, end, l, r);
            return leftSum + rightSum;
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int Q = sc.nextInt();
        int K = sc.nextInt();

        int[] arr = new int[N];
        for (int i = 0; i < N; i++) {
            arr[i] = sc.nextInt();
        }

        SegmentTree st = new SegmentTree(arr, K);

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < Q; i++) {
            int type = sc.nextInt();
            if (type == 1) {
                int idx = sc.nextInt() - 1;
                int val = sc.nextInt();
                st.update(idx, val);
            } else {
                int L = sc.nextInt() - 1;
                int R = sc.nextInt() - 1;
                long result = st.query(L, R);
                sb.append(result).append("\n");
            }
        }

        System.out.print(sb.toString());
        sc.close();
    }
}
