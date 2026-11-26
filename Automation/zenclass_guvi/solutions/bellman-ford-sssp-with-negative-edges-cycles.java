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
        int N = Integer.parseInt(parts[0]);
        int M = Integer.parseInt(parts[1]);
        int S = Integer.parseInt(parts[2]);

        List<Edge> edges = new ArrayList<>();
        for (int i = 0; i < M; i++) {
            parts = br.readLine().trim().split("\\s+");
            int u = Integer.parseInt(parts[0]);
            int v = Integer.parseInt(parts[1]);
            int w = Integer.parseInt(parts[2]);
            edges.add(new Edge(u, v, w));
        }

        final long INF = Long.MAX_VALUE / 2;
        long[] dist = new long[N];
        Arrays.fill(dist, INF);
        dist[S] = 0;

        // Bellman-Ford algorithm
        boolean changed = true;
        int iter = 0;
        while (iter < N - 1 && changed) {
            changed = false;
            for (Edge e : edges) {
                if (dist[e.u] != INF && dist[e.v] > dist[e.u] + e.w) {
                    dist[e.v] = dist[e.u] + e.w;
                    changed = true;
                }
            }
            iter++;
        }

        // Check for negative cycle
        boolean negativeCycle = false;
        for (Edge e : edges) {
            if (dist[e.u] != INF && dist[e.v] > dist[e.u] + e.w) {
                negativeCycle = true;
                break;
            }
        }

        if (negativeCycle) {
            System.out.println("NEGATIVE CYCLE");
        } else {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < N; i++) {
                if (i > 0) sb.append(' ');
                if (dist[i] == INF) {
                    sb.append("INF");
                } else {
                    sb.append(dist[i]);
                }
            }
            System.out.println(sb.toString());
        }
    }
}
