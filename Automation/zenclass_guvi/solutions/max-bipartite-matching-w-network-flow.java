import java.io.*;
import java.util.*;

public class Main {
    static class Dinic {
        int V;
        List<Integer>[] adj;
        int[][] cap;
        int[][] flow;
        int[][] dir;
        
        @SuppressWarnings("unchecked")
        public Dinic(int V) {
            this.V = V;
            adj = new List[V];
            for (int i = 0; i < V; i++) adj[i] = new ArrayList<>();
            cap = new int[V][V];
            flow = new int[V][V];
            dir = new int[V][V];
        }
        
        public void addEdge(int from, int to, int c) {
            adj[from].add(to);
            adj[to].add(from);
            cap[from][to] += c;
            if (cap[to][from] == 0) {
                dir[from][to] = adj[from].size() - 1;
                dir[to][from] = adj[to].size() - 1;
            }
        }
        
        public int maxFlow(int s, int t) {
            int total = 0;
            int[][] next = new int[V][2];
            while (true) {
                int[] level = bfs(s, t, next);
                if (level[t] < 0) break;
                Arrays.fill(next, new int[2]);
                int f;
                while ((f = dfs(s, t, Integer.MAX_VALUE, level, next)) > 0) {
                    total += f;
                }
            }
            return total;
        }
        
        private int[] bfs(int s, int t, int[][] next) {
            int[] level = new int[V];
            Arrays.fill(level, -1);
            Queue<Integer> q = new ArrayDeque<>();
            level[s] = 0;
            q.offer(s);
            while (!q.isEmpty()) {
                int u = q.poll();
                for (int v : adj[u]) {
                    if (level[v] < 0 && cap[u][v] - flow[u][v] > 0) {
                        level[v] = level[u] + 1;
                        q.offer(v);
                    }
                }
            }
            return level;
        }
        
        private int dfs(int u, int t, int flowVal, int[] level, int[][] next) {
            if (u == t) return flowVal;
            for (int i = next[u][0]; i < adj[u].size(); i++) {
                int v = adj[u].get(i);
                if (level[v] == level[u] + 1 && cap[u][v] - flow[u][v] > 0) {
                    int f = dfs(v, t, Math.min(flowVal, cap[u][v] - flow[u][v]), level, next);
                    if (f > 0) {
                        flow[u][v] += f;
                        flow[v][u] -= f;
                        next[u][0] = i;
                        return f;
                    }
                }
            }
            next[u][0] = adj[u].size();
            return 0;
        }
    }
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int N = Integer.parseInt(parts[0]);
        int M = Integer.parseInt(parts[1]);
        int E = Integer.parseInt(br.readLine().trim());
        
        int source = 0;
        int sink = N + M + 1;
        int totalNodes = sink + 1;
        
        Dinic dinic = new Dinic(totalNodes);
        
        for (int i = 1; i <= N; i++) {
            dinic.addEdge(source, i, 1);
        }
        
        for (int i = 1; i <= M; i++) {
            dinic.addEdge(N + i, sink, 1);
        }
        
        for (int i = 0; i < E; i++) {
            parts = br.readLine().trim().split("\\s+");
            int u = Integer.parseInt(parts[0]);
            int v = Integer.parseInt(parts[1]);
            dinic.addEdge(u, N + v, 1);
        }
        
        int result = dinic.maxFlow(source, sink);
        System.out.println(result);
    }
}
