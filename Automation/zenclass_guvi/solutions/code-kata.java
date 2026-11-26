import java.io.*;
import java.util.*;

public class Main {
    static class SegmentTree {
        int n;
        int[][] tree;
        
        public SegmentTree(int[] arr) {
            n = arr.length;
            int height = (int) Math.ceil(Math.log(n) / Math.log(2)) + 1;
            int size = 1 << height;
            tree = new int[size][];
            build(arr, 1, 0, n - 1);
        }
        
        private void build(int[] arr, int node, int start, int end) {
            if (start == end) {
                tree[node] = new int[]{arr[start]};
                return;
            }
            int mid = (start + end) / 2;
            build(arr, 2 * node, start, mid);
            build(arr, 2 * node + 1, mid + 1, end);
            tree[node] = merge(tree[2 * node], tree[2 * node + 1]);
        }
        
        private int[] merge(int[] left, int[] right) {
            int[] merged = new int[left.length + right.length];
            int i = 0, j = 0, k = 0;
            while (i < left.length && j < right.length) {
                if (left[i] <= right[j]) {
                    merged[k++] = left[i++];
                } else {
                    merged[k++] = right[j++];
                }
            }
            while (i < left.length) merged[k++] = left[i++];
            while (j < right.length) merged[k++] = right[j++];
            return merged;
        }
        
        public void update(int idx, int val) {
            update(1, 0, n - 1, idx, val);
        }
        
        private void update(int node, int start, int end, int idx, int val) {
            if (start == end) {
                tree[node][0] = val;
                return;
            }
            int mid = (start + end) / 2;
            if (idx <= mid) {
                update(2 * node, start, mid, idx, val);
            } else {
                update(2 * node + 1, mid + 1, end, idx, val);
            }
            tree[node] = merge(tree[2 * node], tree[2 * node + 1]);
        }
        
        public int query(int l, int r, int x) {
            return query(1, 0, n - 1, l, r, x);
        }
        
        private int query(int node, int start, int end, int l, int r, int x) {
            if (r < start || l > end) {
                return 0;
            }
            if (l <= start && end <= r) {
                return countGreaterThan(tree[node], x);
            }
            int mid = (start + end) / 2;
            int leftCount = query(2 * node, start, mid, l, r, x);
            int rightCount = query(2 * node + 1, mid + 1, end, l, r, x);
            return leftCount + rightCount;
        }
        
        private int countGreaterThan(int[] sorted, int x) {
            int low = 0, high = sorted.length;
            while (low < high) {
                int mid = (low + high) / 2;
                if (sorted[mid] <= x) {
                    low = mid + 1;
                } else {
                    high = mid;
                }
            }
            return sorted.length - low;
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
        
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < q; i++) {
            int type = sc.nextInt();
            if (type == 1) {
                int idx = sc.nextInt();
                int val = sc.nextInt();
                st.update(idx, val);
            } else {
                int l = sc.nextInt();
                int r = sc.nextInt();
                int x = sc.nextInt();
                int count = st.query(l, r, x);
                sb.append(count).append('\n');
            }
        }
        System.out.print(sb.toString());
        sc.close();
    }
}
