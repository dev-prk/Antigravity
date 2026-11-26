import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        long expected = (long) n * (n + 1) / 2;
        long sum = 0;
        while (st.hasMoreTokens()) {
            sum += Long.parseLong(st.nextToken());
        }
        System.out.println(expected - sum);
    }
}
