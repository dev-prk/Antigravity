import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        FastScanner fs = new FastScanner(System.in);
        int N;
        try {
            N = fs.nextInt();
        } catch (Exception e) {
            return;
        }
        int M = fs.nextInt();
        if (N == 0) {
            System.out.println(0);
            System.out.println();
            return;
        }
        int[] dur = new int[N + 1];
        for (int i = 1; i <= N; i++) {
            dur[i] = fs.nextInt();
        }
        @SuppressWarnings("unchecked")
        ArrayList<Integer>[] adj = new ArrayList[N + 1];
        int[] indeg = new int[N + 1];
        for (int i = 1; i <= N; i++) adj[i] = new ArrayList<>();
        for (int i = 0; i < M; i++) {
            int u = fs.nextInt();
            int v = fs.nextInt();
            adj[u].add(v);
            indeg[v]++;
        }

        int[] dp = new int[N + 1];
        int[] prev = new int[N + 1];
        Arrays.fill(prev, -1);
        ArrayDeque<Integer> q = new ArrayDeque<>();
        for (int i = 1; i <= N; i++) {
            if (indeg[i] == 0) {
                q.add(i);
                dp[i] = dur[i];
            }
        }
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : adj[u]) {
                if (dp[v] < dp[u] + dur[v]) {
                    dp[v] = dp[u] + dur[v];
                    prev[v] = u;
                }
                indeg[v]--;
                if (indeg[v] == 0) {
                    q.add(v);
                }
            }
        }

        int maxNode = 1;
        int maxVal = dp[1];
        for (int i = 2; i <= N; i++) {
            if (dp[i] > maxVal) {
                maxVal = dp[i];
                maxNode = i;
            }
        }

        List<Integer> path = new ArrayList<>();
        int cur = maxNode;
        while (cur != -1) {
            path.add(cur);
            cur = prev[cur];
        }
        Collections.reverse(path);

        StringBuilder sb = new StringBuilder();
        sb.append(maxVal).append('\n');
        for (int i = 0; i < path.size(); i++) {
            sb.append(path.get(i));
            if (i + 1 < path.size()) sb.append(' ');
        }
        System.out.print(sb.toString());
    }

    static class FastScanner {
        private final InputStream in;
        private final byte[] buffer = new byte[1 << 16];
        private int ptr = 0, len = 0;

        FastScanner(InputStream is) {
            in = is;
        }

        private int readByte() throws IOException {
            if (ptr >= len) {
                len = in.read(buffer);
                ptr = 0;
                if (len <= 0) return -1;
            }
            return buffer[ptr++];
        }

        int nextInt() throws IOException {
            int c, sign = 1, val = 0;
            do {
                c = readByte();
            } while (c <= ' ' && c != -1);
            if (c == '-') {
                sign = -1;
                c = readByte();
            }
            while (c > ' ') {
                val = val * 10 + (c - '0');
                c = readByte();
            }
            return val * sign;
        }
    }
}
