import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String nStr = br.readLine();
        if (nStr == null || nStr.isEmpty()) {
            return;
        }
        int n = Integer.parseInt(nStr.trim());
        if (n <= 0) {
            return;
        }
        
        Map<String, List<String>> groups = new HashMap<>();
        for (int i = 0; i < n; i++) {
            String word = br.readLine();
            if (word != null) {
                word = word.trim();
            } else {
                word = "";
            }
            String key = getKey(word);
            groups.computeIfAbsent(key, k -> new ArrayList<>()).add(word);
        }
        
        List<List<String>> result = new ArrayList<>(groups.values());
        // Sort each group by first element for consistent output
        Collections.sort(result, (a, b) -> a.get(0).compareTo(b.get(0)));
        
        StringBuilder sb = new StringBuilder();
        for (List<String> group : result) {
            if (sb.length() > 0) sb.append('\n');
            for (int i = 0; i < group.size(); i++) {
                if (i > 0) sb.append(' ');
                sb.append(group.get(i));
            }
        }
        System.out.print(sb.toString());
    }
    
    private static String getKey(String s) {
        char[] arr = s.toCharArray();
        Arrays.sort(arr);
        return new String(arr);
    }
}
