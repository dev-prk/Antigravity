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
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(parts[0]);
        int m = Integer.parseInt(parts[1]);
        
        if (n == 0 || m == 0) {
            System.out.println("NO");
            return;
        }
        
        Edge[] edges = new Edge[m];
        for (int i = 0; i < m; i++) {
            parts = br.readLine().trim().split("\\s+");
            int u = Integer.parseInt(parts[0]);
            int v = Integer.parseInt(parts[1]);
            int w = Integer.parseInt(parts[2]);
            edges[i] = new Edge(u, v, w);
        }
        
        // Initialize distances
        long[] dist = new long[n + 1];
        Arrays.fill(dist, 0);
        
        // Relax all edges n-1 times
        for (int i = 0; i < n - 1; i++) {
            for (Edge e : edges) {
                if (dist[e.u] + e.w < dist[e.v]) {
                    dist[e.v] = dist[e.u] + e.w;
                }
            }
        }
        
        // Check for negative weight cycle
        boolean hasNegativeCycle = false;
        for (Edge e : edges) {
            if (dist[e.u] + e.w < dist[e.v]) {
                hasNegativeCycle = true;
                break;
            }
        }
        
        System.out.println(hasNegativeCycle ? "YES" : "NO");
    }
}
