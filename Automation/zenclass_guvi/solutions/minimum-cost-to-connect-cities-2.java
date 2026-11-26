import java.io.*;
import java.util.*;

public class Main {
    static class Edge implements Comparable<Edge> {
        int u, v, w;
        Edge(int u, int v, int w) {
            this.u = u; this.v = v; this.w = w;
        }
        public int compareTo(Edge other) {
            return Integer.compare(this.w, other.w);
        }
    }
    
    static class UnionFind {
        int[] parent, rank;
        UnionFind(int n) {
            parent = new int[n + 1];
            rank = new int[n + 1];
            for (int i = 1; i <= n; i++) parent[i] = i;
        }
        int find(int x) {
            if (parent[x] != x) parent[x] = find(parent[x]);
            return parent[x];
        }
        boolean union(int x, int y) {
            int rx = find(x), ry = find(y);
            if (rx == ry) return false;
            if (rank[rx] < rank[ry]) {
                parent[rx] = ry;
            } else if (rank[rx] > rank[ry]) {
                parent[ry] = rx;
            } else {
                parent[ry] = rx;
                rank[rx]++;
            }
            return true;
        }
    }
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(parts[0]);
        int m = Integer.parseInt(parts[1]);
        
        if (n == 0 || m == 0) {
            System.out.println(-1);
            return;
        }
        
        List<Edge> edges = new ArrayList<>();
        for (int i = 0; i < m; i++) {
            parts = br.readLine().trim().split("\\s+");
            int u = Integer.parseInt(parts[0]);
            int v = Integer.parseInt(parts[1]);
            int w = Integer.parseInt(parts[2]);
            edges.add(new Edge(u, v, w));
        }
        
        Collections.sort(edges);
        
        UnionFind uf = new UnionFind(n);
        long totalCost = 0;
        int edgesUsed = 0;
        
        for (Edge e : edges) {
            if (uf.union(e.u, e.v)) {
                totalCost += e.w;
                edgesUsed++;
                if (edgesUsed == n - 1) break;
            }
        }
        
        if (edgesUsed != n - 1) {
            System.out.println(-1);
        } else {
            System.out.println(totalCost);
        }
    }
}
