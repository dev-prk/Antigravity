import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        sc.nextLine(); // consume newline
        
        Map<String, Integer> map = new LinkedHashMap<>();
        
        for (int i = 0; i < n; i++) {
            String line = sc.nextLine().trim();
            String[] parts = line.split("\\s+");
            String key = parts[0];
            int value = Integer.parseInt(parts[1]);
            
            map.put(key, map.getOrDefault(key, 0) + value);
        }
        
        for (Map.Entry<String, Integer> entry : map.entrySet()) {
            System.out.println(entry.getKey() + " " + entry.getValue());
        }
        
        sc.close();
    }
}
