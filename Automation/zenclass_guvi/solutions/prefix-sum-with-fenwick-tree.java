import java.io.*;
import java.util.*;

public class Main {
    static class FenwickTree {
        private int[] tree;
        private int n;

        public FenwickTree(int size) {
            n = size;
            tree = new int[n + 1];
        }

        public void update(int index, int delta) {
            while (index <= n) {
                tree[index] += delta;
                index += index & (-index);
            }
        }

        public int query(int index) {
            int sum = 0;
            while (index > 0) {
                sum += tree[index];
                index -= index & (-index);
            }
            return sum;
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        int q = sc.nextInt();
        
        int[] arr = new int[n + 1];
        FenwickTree ft = new FenwickTree(n);
        
        for (int i = 1; i <= n; i++) {
            arr[i] = sc.nextInt();
            ft.update(i, arr[i]);
        }
        
        StringBuilder sb = new StringBuilder();
        
        for (int i = 0; i < q; i++) {
            int type = sc.nextInt();
            
            if (type == 1) {
                int x = sc.nextInt();
                int y = sc.nextInt();
                int delta = y - arr[x];
                arr[x] = y;
                ft.update(x, delta);
            } else {
                int x = sc.nextInt();
                sb.append(ft.query(x)).append('\n');
            }
        }
        
        System.out.print(sb.toString());
        sc.close();
    }
}
