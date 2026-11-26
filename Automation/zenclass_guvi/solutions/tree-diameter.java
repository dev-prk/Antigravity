import java.io.*;
import java.util.*;

public class Main {
    static class Scanner {
        private final BufferedInputStream bis;
        private final byte[] buffer = new byte[1024];
        private int ptr = 0, len = 0;

        public Scanner(InputStream in) {
            bis = new BufferedInputStream(in);
        }

        private int readByte() throws IOException {
            if (len == -1) throw new EOFException();
            if (ptr >= len) {
                len = bis.read(buffer);
                ptr = 0;
                if (len <= 0) return -1;
            }
            return buffer[ptr++];
        }

        public int nextInt() throws IOException {
            int c, val = 0, sign = 1;
            while ((c = readByte()) != -1 && c <= ' ');
            if (c == '-') {
                sign = -1;
                c = readByte();
            }
            do {
                val = val * 10 + (c - '0');
                c = readByte();
            } while (c > ' ');
            return val * sign;
        }
    }

    static int n;
    static ArrayList<Integer>[] adj;

    static int[] bfs(int start) {
        int[] dist = new int[n + 1];
        Arrays.fill(dist, -1);
        Queue<Integer> q = new ArrayDeque<>();
        dist[start] = 0;
        q.offer(start);
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : adj[u]) {
                if (dist[v] == -1) {
                    dist[v] = dist[u] + 1;
                    q.offer(v);
                }
            }
        }
        return dist;
    }

    public static void main(String[] args) throws Exception {
        Scanner sc = new Scanner(System.in);
        n = sc.nextInt();
        if (n <= 1) {
            System.out.println(0);
            return;
        }
        adj = new ArrayList[n + 1];
        for (int i = 0; i <= n; i++) {
            adj[i] = new ArrayList<>();
        }
        for (int i = 0; i < n - 1; i++) {
            int u = sc.nextInt();
            int v = sc.nextInt();
            adj[u].add(v);
            adj[v].add(u);
        }

        int[] dist1 = bfs(1);
        int farthest1 = 1;
        for (int i = 1; i <= n; i++) {
            if (dist1[i] > dist1[farthest1]) {
                farthest1 = i;
            }
        }

        int[] dist2 = bfs(farthest1);
        int farthest2 = farthest1;
        for (int i = 1; i <= n; i++) {
            if (dist2[i] > dist2[farthest2]) {
                farthest2 = i;
            }
        }

        System.out.println(dist2[farthest2]);
    }
}
