import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        
        Map<Character, Integer> count = new LinkedHashMap<>();
        for (char c : s.toCharArray()) {
            count.put(c, count.getOrDefault(c, 0) + 1);
        }
        
        List<Character> duplicates = new ArrayList<>();
        for (Map.Entry<Character, Integer> entry : count.entrySet()) {
            if (entry.getValue() > 1) {
                duplicates.add(entry.getKey());
            }
        }
        
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < duplicates.size(); i++) {
            if (i > 0) sb.append(' ');
            sb.append(duplicates.get(i));
        }
        System.out.println(sb.toString());
    }
}
