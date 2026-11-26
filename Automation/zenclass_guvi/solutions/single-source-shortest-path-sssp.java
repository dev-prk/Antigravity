import java.io.*;
import java.util.*;

public class Main {
    static class Edge {
        int v, w;
        Edge(int v, int w) {
            this.v = v;
            this.w = w;
        }
    }
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int N = Integer.parseInt(parts[0]);
        int M = Integer.parseInt(parts[1]);
        int S = Integer.parseInt(parts[2]);
        
        @SuppressWarnings("unchecked")
        List<Edge>[] adj = new ArrayList[N + 1];
        for (int i = 1; i <= N; i++) {
            adj[i] = new ArrayList<>();
        }
        
        for (int i = 0; i < M; i++) {
            parts = br.readLine().trim().split("\\s+");
            int u = Integer.parseInt(parts[0]);
            int v = Integer.parseInt(parts[1]);
            int w = Integer.parseInt(parts[2]);
            adj[u].add(new Edge(v, w));
        }
        
        long[] dist = new long[N + 1];
        Arrays.fill(dist, Long.MAX_VALUE);
        dist[S] = 0;
        
        int[] inQueue = new int[N + 1];
        Arrays.fill(inQueue, 0);
        Deque<Integer> q = new ArrayDeque<>();
        q.add(S);
        inQueue[S] = 1;
        
        while (!q.isEmpty()) {
            int u = q.poll();
            inQueue[u] = 0;
            for (Edge e : adj[u]) {
                if (dist[e.v] > dist[u] + e.w) {
                    dist[e.v] = dist[u] + e.w;
                    if (inQueue[e.v] == 0) {
                        q.add(e.v);
                        inQueue[e.v] = 1;
                    }
                }
            }
        }
        
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= N; i++) {
            if (i > 1) sb.append(' ');
            if (dist[i] == Long.MAX_VALUE) {
                sb.append(-1);
            } else {
                sb.append(dist[i]);
            }
        }
        sb.append('\n');
        System.out.print(sb.toString());
    }
}
