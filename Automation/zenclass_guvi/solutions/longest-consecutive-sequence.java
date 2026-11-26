import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String nStr = br.readLine();
        if (nStr == null || nStr.trim().isEmpty()) {
            System.out.println(0);
            return;
        }
        int n = Integer.parseInt(nStr.trim());
        if (n == 0) {
            System.out.println(0);
            return;
        }
        
        String[] tokens = br.readLine().trim().split("\\s+");
        Set<Integer> set = new HashSet<>();
        for (int i = 0; i < n && i < tokens.length; i++) {
            set.add(Integer.parseInt(tokens[i]));
        }
        
        int max = 0;
        for (int num : set) {
            if (!set.contains(num - 1)) {
                int current = num;
                int streak = 1;
                while (set.contains(current + 1)) {
                    current++;
                    streak++;
                }
                max = Math.max(max, streak);
            }
        }
        
        System.out.println(max);
    }
}
