import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        int n = Integer.parseInt(br.readLine().trim());
        Set<Integer> set = new TreeSet<>(Collections.reverseOrder());
        
        if (n > 0) {
            String[] parts = br.readLine().trim().split("\\s+");
            for (String part : parts) {
                if (!part.isEmpty()) {
                    set.add(Integer.parseInt(part));
                }
            }
        }
        
        int m = Integer.parseInt(br.readLine().trim());
        if (m > 0) {
            String[] parts = br.readLine().trim().split("\\s+");
            for (String part : parts) {
                if (!part.isEmpty()) {
                    set.add(Integer.parseInt(part));
                }
            }
        }
        
        List<Integer> result = new ArrayList<>(set);
        Collections.sort(result, Collections.reverseOrder());
        
        StringBuilder sb = new StringBuilder();
        sb.append('[');
        for (int i = 0; i < result.size(); i++) {
            sb.append(result.get(i));
            if (i < result.size() - 1) {
                sb.append(", ");
            }
        }
        sb.append(']');
        
        System.out.println(sb.toString());
    }
}
