import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int[] arr = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            arr[i] = Integer.parseInt(parts[i]);
        }
        int target = Integer.parseInt(br.readLine().trim());
        
        List<Integer> indices = new ArrayList<>();
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == target) {
                indices.add(i);
            }
        }
        
        if (indices.isEmpty()) {
            System.out.println(-1);
        } else {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < indices.size(); i++) {
                if (i > 0) sb.append(' ');
                sb.append(indices.get(i));
            }
            sb.append(' ');
            System.out.println(sb.toString());
        }
    }
}
