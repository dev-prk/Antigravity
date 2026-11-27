import java.io.*;
import java.util.*;

public class Main {
    static class Edge {
        int to, rev;
        long cap;
        
        Edge(int to, long cap, int rev) {
            this.to = to;
            this.cap = cap;
            this.rev = rev;
        }
    }
    
    static List<Edge>[] graph;
    static int[] level;
    static int[] ptr;
    
    static void addEdge(int from, int to, long cap) {
        Edge e1 = new Edge(to, cap, graph[to].size());
        Edge e2 = new Edge(from, 0, graph[from].size());
        graph[from].add(e1);
        graph[to].add(e2);
    }
    
    static boolean bfs(int s, int t, int n) {
        Arrays.fill(level, -1);
        Queue<Integer> q = new LinkedList<>();
        level[s] = 0;
        q.offer(s);
        
        while (!q.isEmpty()) {
            int u = q.poll();
            for (Edge e : graph[u]) {
                if (e.cap > 0 && level[e.to] == -1) {
                    level[e.to] = level[u] + 1;
                    q.offer(e.to);
                }
            }
        }
        return level[t] != -1;
    }
    
    static long dfs(int u, int t, long flow) {
        if (u == t) return flow;
        for (int i = ptr[u]; i < graph[u].size(); i++) {
            Edge e = graph[u].get(i);
            if (e.cap > 0 && level[e.to] == level[u] + 1) {
                long pushed = dfs(e.to, t, Math.min(flow, e.cap));
                if (pushed > 0) {
                    e.cap -= pushed;
                    graph[e.to].get(e.rev).cap += pushed;
                    return pushed;
                }
            }
            ptr[u]++;
        }
        return 0;
    }
    
    static long maxFlow(int s, int t, int n) {
        long totalFlow = 0;
        
        while (bfs(s, t, n)) {
            Arrays.fill(ptr, 0);
            while (true) {
                long flow = dfs(s, t, Long.MAX_VALUE);
                if (flow == 0) break;
                totalFlow += flow;
            }
        }
        
        return totalFlow;
    }
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(parts[0]);
        int m = Integer.parseInt(parts[1]);
        int q = Integer.parseInt(parts[2]);
        
        graph = new ArrayList[n + 1];
        level = new int[n + 1];
        ptr = new int[n + 1];
        
        for (int i = 0; i <= n; i++) {
            graph[i] = new ArrayList<>();
        }
        
        for (int i = 0; i < m; i++) {
            parts = br.readLine().trim().split("\\s+");
            int u = Integer.parseInt(parts[0]);
            int v = Integer.parseInt(parts[1]);
            long c = Long.parseLong(parts[2]);
            addEdge(u, v, c);
        }
        
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < q; i++) {
            parts = br.readLine().trim().split("\\s+");
            int s = Integer.parseInt(parts[0]);
            int t = Integer.parseInt(parts[1]);
            long flow = maxFlow(s, t, n);
            sb.append(flow);
            if (i < q - 1) sb.append("\n");
        }
        
        System.out.print(sb.toString());
    }
}
