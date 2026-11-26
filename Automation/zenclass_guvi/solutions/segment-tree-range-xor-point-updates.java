import java.util.Scanner;

public class Main {
    static class SegmentTree {
        private int[] tree;
        private int n;

        public SegmentTree(int[] arr) {
            n = arr.length;
            tree = new int[4 * n];
            build(arr, 0, 0, n - 1);
        }

        private void build(int[] arr, int node, int start, int end) {
            if (start == end) {
                tree[node] = arr[start];
            } else {
                int mid = (start + end) / 2;
                build(arr, 2 * node + 1, start, mid);
                build(arr, 2 * node + 2, mid + 1, end);
                tree[node] = tree[2 * node + 1] ^ tree[2 * node + 2];
            }
        }

        public int query(int l, int r) {
            return query(0, 0, n - 1, l, r);
        }

        private int query(int node, int start, int end, int l, int r) {
            if (r < start || l > end) {
                return 0;
            }
            if (l <= start && end <= r) {
                return tree[node];
            }
            int mid = (start + end) / 2;
            int leftXor = query(2 * node + 1, start, mid, l, r);
            int rightXor = query(2 * node + 2, mid + 1, end, l, r);
            return leftXor ^ rightXor;
        }

        public void update(int idx, int val) {
            update(0, 0, n - 1, idx, val);
        }

        private void update(int node, int start, int end, int idx, int val) {
            if (start == end) {
                tree[node] = val;
            } else {
                int mid = (start + end) / 2;
                if (idx <= mid) {
                    update(2 * node + 1, start, mid, idx, val);
                } else {
                    update(2 * node + 2, mid + 1, end, idx, val);
                }
                tree[node] = tree[2 * node + 1] ^ tree[2 * node + 2];
            }
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        int q = sc.nextInt();
        
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        
        SegmentTree st = new SegmentTree(arr);
        
        for (int i = 0; i < q; i++) {
            int type = sc.nextInt();
            if (type == 1) {
                int l = sc.nextInt() - 1;
                int r = sc.nextInt() - 1;
                System.out.println(st.query(l, r));
            } else if (type == 2) {
                int x = sc.nextInt() - 1;
                int v = sc.nextInt();
                st.update(x, v);
            }
        }
        
        sc.close();
    }
}
