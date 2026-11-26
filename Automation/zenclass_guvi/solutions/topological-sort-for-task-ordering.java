import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int N = sc.nextInt();
        int M = sc.nextInt();
        
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            adj.add(new ArrayList<>());
        }
        
        int[] inDegree = new int[N];
        
        for (int i = 0; i < M; i++) {
            int a = sc.nextInt();
            int b = sc.nextInt();
            adj.get(a).add(b);
            inDegree[b]++;
        }
        
        Queue<Integer> queue = new LinkedList<>();
        for (int i = 0; i < N; i++) {
            if (inDegree[i] == 0) {
                queue.offer(i);
            }
        }
        
        List<Integer> result = new ArrayList<>();
        
        while (!queue.isEmpty()) {
            int curr = queue.poll();
            result.add(curr);
            
            for (int next : adj.get(curr)) {
                inDegree[next]--;
                if (inDegree[next] == 0) {
                    queue.offer(next);
                }
            }
        }
        
        if (result.size() != N) {
            System.out.println("Impossible");
        } else {
            for (int i = 0; i < result.size(); i++) {
                if (i > 0) System.out.print(" ");
                System.out.print(result.get(i));
            }
            System.out.println();
        }
        
        sc.close();
    }
}
