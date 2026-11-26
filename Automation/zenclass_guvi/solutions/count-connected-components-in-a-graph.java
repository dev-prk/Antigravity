import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

public class Main {
    static class DSU {
        int[] parent;
        int[] rank;
        int count;

        DSU(int n) {
            parent = new int[n];
            rank = new int[n];
            count = n;
            for (int i = 0; i < n; i++) {
                parent[i] = i;
            }
        }

        int find(int x) {
            while (parent[x] != x) {
                parent[x] = parent[parent[x]];
                x = parent[x];
            }
            return x;
        }

        void union(int a, int b) {
            int ra = find(a);
            int rb = find(b);
            if (ra == rb) return;
            if (rank[ra] < rank[rb]) {
                parent[ra] = rb;
            } else if (rank[ra] > rank[rb]) {
                parent[rb] = ra;
            } else {
                parent[rb] = ra;
                rank[ra]++;
            }
            count--;
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String firstLine = br.readLine();
        if (firstLine == null || firstLine.trim().isEmpty()) {
            System.out.println(0);
            return;
        }
        StringTokenizer st = new StringTokenizer(firstLine);
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        DSU dsu = new DSU(n);

        for (int i = 0; i < m; i++) {
            String edgeLine = br.readLine();
            if (edgeLine == null) break;
            StringTokenizer est = new StringTokenizer(edgeLine);
            int u = Integer.parseInt(est.nextToken());
            int v = Integer.parseInt(est.nextToken());
            dsu.union(u, v);
        }

        System.out.println(dsu.count);
    }
}
