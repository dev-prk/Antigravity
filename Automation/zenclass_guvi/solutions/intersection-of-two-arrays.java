import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        int n = Integer.parseInt(br.readLine().trim());
        Set<Integer> set1 = new HashSet<>();
        if (n > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            while (st.hasMoreTokens()) {
                set1.add(Integer.parseInt(st.nextToken()));
            }
        }
        
        int m = Integer.parseInt(br.readLine().trim());
        Set<Integer> set2 = new HashSet<>();
        if (m > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            while (st.hasMoreTokens()) {
                set2.add(Integer.parseInt(st.nextToken()));
            }
        }
        
        set1.retainAll(set2);
        
        StringBuilder sb = new StringBuilder();
        for (int num : set1) {
            if (sb.length() > 0) sb.append(' ');
            sb.append(num);
        }
        
        System.out.println(sb.toString());
    }
}
