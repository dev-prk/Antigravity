import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null || line.isEmpty()) {
            System.out.println(0);
            return;
        }
        int n = Integer.parseInt(line.trim());
        if (n <= 0) {
            System.out.println(0);
            return;
        }
        long sum = 0;
        int count = 0;
        while (count < n && (line = br.readLine()) != null) {
            line = line.trim();
            if (line.isEmpty()) continue;
            StringTokenizer st = new StringTokenizer(line);
            while (st.hasMoreTokens() && count < n) {
                sum += Long.parseLong(st.nextToken());
                count++;
            }
        }
        System.out.println(sum);
    }
}
