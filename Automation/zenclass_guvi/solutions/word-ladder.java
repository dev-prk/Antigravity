import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String beginWord = br.readLine().trim();
        String endWord = br.readLine().trim();
        int n = Integer.parseInt(br.readLine().trim());
        
        Set<String> wordSet = new HashSet<>();
        for (int i = 0; i < n; i++) {
            wordSet.add(br.readLine().trim());
        }
        
        if (!wordSet.contains(endWord)) {
            System.out.println(0);
            return;
        }
        
        if (beginWord.equals(endWord)) {
            System.out.println(1);
            return;
        }
        
        int wordLen = beginWord.length();
        Map<String, List<String>> adjList = new HashMap<>();
        for (String word : wordSet) {
            for (int i = 0; i < wordLen; i++) {
                String pattern = word.substring(0, i) + "*" + word.substring(i + 1);
                adjList.computeIfAbsent(pattern, k -> new ArrayList<>()).add(word);
            }
        }
        
        Queue<String> queue = new LinkedList<>();
        Set<String> visited = new HashSet<>();
        queue.offer(beginWord);
        visited.add(beginWord);
        int level = 1;
        
        while (!queue.isEmpty()) {
            int size = queue.size();
            for (int i = 0; i < size; i++) {
                String curr = queue.poll();
                for (int j = 0; j < wordLen; j++) {
                    String pattern = curr.substring(0, j) + "*" + curr.substring(j + 1);
                    List<String> neighbors = adjList.getOrDefault(pattern, new ArrayList<>());
                    for (String neighbor : neighbors) {
                        if (neighbor.equals(endWord)) {
                            System.out.println(level + 1);
                            return;
                        }
                        if (!visited.contains(neighbor)) {
                            visited.add(neighbor);
                            queue.offer(neighbor);
                        }
                    }
                }
            }
            level++;
        }
        
        System.out.println(0);
    }
}
