import java.io.*;
import java.util.*;

public class Main {
    static class SegmentTree {
        int n;
        long[] minTree;
        long[] lazy;
        
        public SegmentTree(int[] arr) {
            n = arr.length;
            minTree = new long[4 * n];
            lazy = new long[4 * n];
            build(arr, 1, 0, n - 1);
        }
        
        private void build(int[] arr, int node, int start, int end) {
            if (start == end) {
                minTree[node] = arr[start];
            } else {
                int mid = (start + end) / 2;
                build(arr, 2 * node, start, mid);
                build(arr, 2 * node + 1, mid + 1, end);
                minTree[node] = Math.min(minTree[2 * node], minTree[2 * node + 1]);
            }
            lazy[node] = 0;
        }
        
        private void push(int node, int start, int end) {
            if (lazy[node] != 0) {
                minTree[node] += lazy[node];
                if (start != end) {
                    lazy[2 * node] += lazy[node];
                    lazy[2 * node + 1] += lazy[node];
                }
                lazy[node] = 0;
            }
        }
        
        private void updateRange(int node, int start, int end, int l, int r, long val) {
            push(node, start, end);
            
            if (start > r || end < l) return;
            
            if (start >= l && end <= r) {
                minTree[node] += val;
                if (start != end) {
                    lazy[2 * node] += val;
                    lazy[2 * node + 1] += val;
                }
                return;
            }
            
            int mid = (start + end) / 2;
            updateRange(2 * node, start, mid, l, r, val);
            updateRange(2 * node + 1, mid + 1, end, l, r, val);
            minTree[node] = Math.min(minTree[2 * node], minTree[2 * node + 1]);
        }
        
        public void update(int l, int r, long val) {
            updateRange(1, 0, n - 1, l, r, val);
        }
        
        private long queryRange(int node, int start, int end, int l, int r) {
            push(node, start, end);
            
            if (start > r || end < l) return Long.MAX_VALUE;
            
            if (start >= l && end <= r) {
                return minTree[node];
            }
            
            int mid = (start + end) / 2;
            long left = queryRange(2 * node, start, mid, l, r);
            long right = queryRange(2 * node + 1, mid + 1, end, l, r);
            return Math.min(left, right);
        }
        
        public long query(int l, int r) {
            return queryRange(1, 0, n - 1, l, r);
        }
    }
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int N = Integer.parseInt(st.nextToken());
        int Q = Integer.parseInt(st.nextToken());
        
        int[] arr = new int[N];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }
        
        SegmentTree stree = new SegmentTree(arr);
        StringBuilder sb = new StringBuilder();
        
        for (int q = 0; q < Q; q++) {
            st = new StringTokenizer(br.readLine());
            int type = Integer.parseInt(st.nextToken());
            
            if (type == 1) {
                int L = Integer.parseInt(st.nextToken()) - 1;
                int R = Integer.parseInt(st.nextToken()) - 1;
                int V = Integer.parseInt(st.nextToken());
                stree.update(L, R, V);
            } else {
                int L = Integer.parseInt(st.nextToken()) - 1;
                int R = Integer.parseInt(st.nextToken()) - 1;
                long result = stree.query(L, R);
                sb.append(result).append('\n');
            }
        }
        
        System.out.print(sb.toString());
    }
}
