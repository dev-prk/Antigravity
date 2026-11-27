import java.io.*;
import java.util.*;

public class Main {
    static class Edge implements Comparable<Edge> {
        int u, v, w;
        Edge(int u, int v, int w) {
            this.u = u; this.v = v; this.w = w;
        }
        public int compareTo(Edge other) {
            return Integer.compare(other.w, this.w); // Descending order
        }
    }

    static int[] parent, rank;

    static int find(int x) {
        if (parent[x] != x) {
            parent[x] = find(parent[x]);
        }
        return parent[x];
    }

    static void union(int x, int y) {
        int px = find(x), py = find(y);
        if (px == py) return;
        if (rank[px] < rank[py]) {
            parent[px] = py;
        } else if (rank[px] > rank[py]) {
            parent[py] = px;
        } else {
            parent[py] = px;
            rank[px]++;
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().split(" ");
        int n = Integer.parseInt(parts[0]);
        int m = Integer.parseInt(parts[1]);
        
        List<Edge> edges = new ArrayList<>();
        for (int i = 0; i < m; i++) {
            parts = br.readLine().split(" ");
            int u = Integer.parseInt(parts[0]);
            int v = Integer.parseInt(parts[1]);
            int w = Integer.parseInt(parts[2]);
            edges.add(new Edge(u, v, w));
        }
        
        // Sort edges in descending order of weight
        Collections.sort(edges);
        
        // Initialize DSU
        parent = new int[n + 1];
        rank = new int[n + 1];
        for (int i = 1; i <= n; i++) {
            parent[i] = i;
            rank[i] = 0;
        }
        
        int mstWeight = 0;
        List<Edge> activeEdges = new ArrayList<>(edges);
        
        // Process edges in descending order
        for (Edge e : edges) {
            boolean canDelete = true;
            int u = e.u, v = e.v;
            
            // Temporarily remove this edge
            Iterator<Edge> it = activeEdges.iterator();
            while (it.hasNext()) {
                Edge curr = it.next();
                if ((curr.u == u && curr.v == v) || (curr.u == v && curr.v == u) ||
                    (curr.u == u && curr.v == v) || (curr.u == v && curr.v == u)) {
                    if (curr.w == e.w) {
                        it.remove();
                        break;
                    }
                }
            }
            
            // Check if graph is still connected
            // Reset DSU
            for (int i = 1; i <= n; i++) {
                parent[i] = i;
                rank[i] = 0;
            }
            
            for (Edge edge : activeEdges) {
                union(edge.u, edge.v);
            }
            
            int root = find(1);
            for (int i = 2; i <= n; i++) {
                if (find(i) != root) {
                    canDelete = false;
                    break;
                }
            }
            
            if (canDelete) {
                // Keep the edge deleted, add its weight to MST
                mstWeight += e.w;
            } else {
                // Restore the edge
                activeEdges.add(e);
            }
        }
        
        // Calculate actual MST weight by summing active edges
        mstWeight = 0;
        for (Edge e : activeEdges) {
            mstWeight += e.w;
        }
        
        System.out.println(mstWeight);
    }
}
