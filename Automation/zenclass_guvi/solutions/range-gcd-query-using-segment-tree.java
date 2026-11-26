import java.io.*;
import java.util.*;

public class Main {
    static class SegmentTree {
        private int[] tree;
        private int n;

        public SegmentTree(int[] arr) {
            n = arr.length;
            tree = new int[4 * n];
            build(arr, 0, 0, n - 1);
        }

        private int gcd(int a, int b) {
            while (b != 0) {
                int temp = b;
                b = a % b;
                a = temp;
            }
            return a;
        }

        private void build(int[] arr, int node, int start, int end) {
            if (start == end) {
                tree[node] = arr[start];
            } else {
                int mid = (start + end) / 2;
                build(arr, 2 * node + 1, start, mid);
                build(arr, 2 * node + 2, mid + 1, end);
                tree[node] = gcd(tree[2 * node + 1], tree[2 * node + 2]);
            }
        }

        public void update(int idx, int val) {
            updateUtil(0, 0, n - 1, idx, val);
        }

        private void updateUtil(int node, int start, int end, int idx, int val) {
            if (start == end) {
                tree[node] = val;
            } else {
                int mid = (start + end) / 2;
                if (idx <= mid) {
                    updateUtil(2 * node + 1, start, mid, idx, val);
                } else {
                    updateUtil(2 * node + 2, mid + 1, end, idx, val);
                }
                tree[node] = gcd(tree[2 * node + 1], tree[2 * node + 2]);
            }
        }

        public int query(int l, int r) {
            return queryUtil(0, 0, n - 1, l, r);
        }

        private int queryUtil(int node, int start, int end, int l, int r) {
            if (r < start || end < l) {
                return 0;
            }
            if (l <= start && end <= r) {
                return tree[node];
            }
            int mid = (start + end) / 2;
            int leftGcd = queryUtil(2 * node + 1, start, mid, l, r);
            int rightGcd = queryUtil(2 * node + 2, mid + 1, end, l, r);
            if (l <= mid && r > mid) {
                return gcd(leftGcd, rightGcd);
            } else if (l <= mid) {
                return leftGcd;
            } else {
                return rightGcd;
            }
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

        SegmentTree segTree = new SegmentTree(arr);
        StringBuilder sb = new StringBuilder();

        for (int i = 0; i < q; i++) {
            st = new StringTokenizer(br.readLine());
            int type = Integer.parseInt(st.nextToken());
            if (type == 1) {
                int idx = Integer.parseInt(st.nextToken());
                int val = Integer.parseInt(st.nextToken());
                segTree.update(idx, val);
            } else {
                int l = Integer.parseInt(st.nextToken());
                int r = Integer.parseInt(st.nextToken());
                sb.append(segTree.query(l, r)).append('\n');
            }
        }

        System.out.print(sb.toString());
    }
}
