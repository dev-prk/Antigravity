import java.io.*;
import java.util.*;

public class Main {
    static int N;
    static int[] value;
    static int[] inTime;
    static int[] outTime;
    static long[] sum;
    static int timer;
    static List<Integer>[] adj;
    static int[][] up;
    static int LOG;
    static int[] depth;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        N = Integer.parseInt(br.readLine().trim());
        value = new int[N + 1];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 1; i <= N; i++) {
            value[i] = Integer.parseInt(st.nextToken());
        }

        adj = new ArrayList[N + 1];
        for (int i = 0; i <= N; i++) {
            adj[i] = new ArrayList<>();
        }

        for (int i = 0; i < N - 1; i++) {
            st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            adj[a].add(b);
            adj[b].add(a);
        }

        inTime = new int[N + 1];
        outTime = new int[N + 1];
        sum = new long[N + 1];
        depth = new int[N + 1];
        LOG = 20;
        up = new int[N + 1][LOG];
        timer = 0;

        dfs(1, -1);

        preprocessLCA();

        int Q = Integer.parseInt(br.readLine().trim());
        StringBuilder sb = new StringBuilder();
        for (int q = 0; q < Q; q++) {
            st = new StringTokenizer(br.readLine());
            int u = Integer.parseInt(st.nextToken());
            int v = Integer.parseInt(st.nextToken());
            long res = getPathSum(u, v);
            sb.append(res).append('\n');
        }
        System.out.print(sb.toString());
    }

    static void dfs(int u, int parent) {
        inTime[u] = ++timer;
        sum[u] = (parent == -1 ? value[u] : sum[parent] + value[u]);
        up[u][0] = parent;
        for (int j = 1; j < LOG; j++) {
            if (up[u][j - 1] != -1) {
                up[u][j] = up[up[u][j - 1]][j - 1];
            } else {
                up[u][j] = -1;
            }
        }

        for (int v : adj[u]) {
            if (v != parent) {
                depth[v] = depth[u] + 1;
                dfs(v, u);
            }
        }
        outTime[u] = timer;
    }

    static void preprocessLCA() {
        for (int j = 1; j < LOG; j++) {
            for (int i = 1; i <= N; i++) {
                if (up[i][j - 1] != -1) {
                    up[i][j] = up[up[i][j - 1]][j - 1];
                } else {
                    up[i][j] = -1;
                }
            }
        }
    }

    static int lca(int u, int v) {
        if (depth[u] < depth[v]) {
            int temp = u;
            u = v;
            v = temp;
        }

        int diff = depth[u] - depth[v];
        for (int j = 0; j < LOG; j++) {
            if ((diff & (1 << j)) != 0) {
                u = up[u][j];
            }
        }

        if (u == v) return u;

        for (int j = LOG - 1; j >= 0; j--) {
            if (up[u][j] != -1 && up[u][j] != up[v][j]) {
                u = up[u][j];
                v = up[v][j];
            }
        }

        return up[u][0];
    }

    static long getPathSum(int u, int v) {
        int l = lca(u, v);
        return sum[u] + sum[v] - 2 * sum[l] + value[l];
    }
}
