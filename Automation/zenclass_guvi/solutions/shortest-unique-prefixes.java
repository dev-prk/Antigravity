import java.io.*;
import java.util.*;

public class Main {
    static class TrieNode {
        TrieNode[] children;
        int count;

        TrieNode() {
            children = new TrieNode[26];
            count = 0;
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        String[] words = new String[n];
        for (int i = 0; i < n; i++) {
            words[i] = br.readLine();
        }

        TrieNode root = new TrieNode();
        for (String word : words) {
            TrieNode current = root;
            for (char c : word.toCharArray()) {
                int idx = c - 'a';
                if (current.children[idx] == null) {
                    current.children[idx] = new TrieNode();
                }
                current = current.children[idx];
                current.count++;
            }
        }

        StringBuilder sb = new StringBuilder();
        for (String word : words) {
            TrieNode current = root;
            StringBuilder prefix = new StringBuilder();
            for (char c : word.toCharArray()) {
                int idx = c - 'a';
                current = current.children[idx];
                prefix.append(c);
                if (current.count == 1) {
                    break;
                }
            }
            sb.append(prefix.toString()).append('\n');
        }

        System.out.print(sb.toString());
    }
}
