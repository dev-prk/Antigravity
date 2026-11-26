import java.io.*;
import java.util.*;

public class Main {
    static class Edge {
        int u, v, w;
        Edge(int u, int v, int w) {
            this.u = u;
            this.v = v;
            this.w = w;
        }
    }
    
    static class UnionFind {
        int[] parent, rank;
        UnionFind(int n) {
            parent = new int[n];
            rank = new int[n];
            for (int i = 0; i < n; i++) parent[i] = i;
        }
        int find(int x) {
            if (parent[x] != x) parent[x] = find(parent[x]);
            return parent[x];
        }
        void union(int x, int y) {
            int rx = find(x), ry = find(y);
            if (rx == ry) return;
            if (rank[rx] < rank[ry]) parent[rx] = ry;
            else if (rank[rx] > rank[ry]) parent[ry] = rx;
            else { parent[ry] = rx; rank[rx]++; }
        }
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] nm = br.readLine().split("\\s+");
        int n = Integer.parseInt(nm[0]);
        int m = Integer.parseInt(nm[1]);
        
        int[][] grid = new int[n][m];
        for (int i = 0; i < n; i++) {
            String[] line = br.readLine().split("\\s+");
            for (int j = 0; j < m; j++) {
                grid[i][j] = Integer.parseInt(line[j]);
            }
        }
        
        int V = n * m;
        List<Edge> edges = new ArrayList<>();
        int[] dr = {-1, 0, 1, 0};
        int[] dc = {0, 1, 0, -1};
        
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                int u = i * m + j;
                for (int d = 0; d < 4; d++) {
                    int ni = i + dr[d], nj = j + dc[d];
                    if (ni >= 0 && ni < n && nj >= 0 && nj < m) {
                        int v = ni * m + nj;
                        int w = grid[i][j] + grid[ni][nj];
                        edges.add(new Edge(u, v, w));
                    }
                }
            }
        }
        
        Collections.sort(edges, Comparator.comparingInt(e -> e.w));
        
        UnionFind uf = new UnionFind(V);
        long mstCost = 0;
        int edgesUsed = 0;
        
        for (Edge e : edges) {
            if (uf.find(e.u) != uf.find(e.v)) {
                uf.union(e.u, e.v);
                mstCost += e.w;
                edgesUsed++;
                if (edgesUsed == V - 1) break;
            }
        }
        
        System.out.println(mstCost);
    }
}
