import java.io.*;
import java.util.*;

public class Main {
    static class TrieNode {
        Map<Character, TrieNode> children;
        boolean isEnd;
        
        TrieNode() {
            children = new HashMap<>();
            isEnd = false;
        }
    }
    
    static class Trie {
        private TrieNode root;
        
        public Trie() {
            root = new TrieNode();
        }
        
        public void insert(String word) {
            TrieNode current = root;
            for (char ch : word.toCharArray()) {
                current.children.putIfAbsent(ch, new TrieNode());
                current = current.children.get(ch);
            }
            current.isEnd = true;
        }
        
        public boolean search(String word) {
            TrieNode node = getNode(word);
            return node != null && node.isEnd;
        }
        
        public boolean startsWith(String prefix) {
            return getNode(prefix) != null;
        }
        
        private TrieNode getNode(String key) {
            TrieNode current = root;
            for (char ch : key.toCharArray()) {
                if (!current.children.containsKey(ch)) {
                    return null;
                }
                current = current.children.get(ch);
            }
            return current;
        }
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        Trie trie = new Trie();
        
        int n = Integer.parseInt(br.readLine().trim());
        
        for (int i = 0; i < n; i++) {
            String line = br.readLine().trim();
            String[] parts = line.split(" ", 2);
            String command = parts[0];
            
            if (command.equals("insert")) {
                String word = parts[1];
                trie.insert(word);
            } else if (command.equals("search")) {
                String word = parts[1];
                System.out.println(trie.search(word));
            } else if (command.equals("startsWith")) {
                String prefix = parts[1];
                System.out.println(trie.startsWith(prefix));
            }
        }
    }
}
