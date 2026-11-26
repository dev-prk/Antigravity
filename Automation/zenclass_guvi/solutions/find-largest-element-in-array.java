import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        
        if (n <= 0) {
            System.out.println(-1);
            return;
        }
        
        StringTokenizer st = new StringTokenizer(br.readLine());
        int max = Integer.MIN_VALUE;
        int count = 0;
        
        while (st.hasMoreTokens() && count < n) {
            int num = Integer.parseInt(st.nextToken());
            if (num > max) {
                max = num;
            }
            count++;
        }
        
        System.out.println(max);
    }
}
