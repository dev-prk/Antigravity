import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        int first = Integer.parseInt(st.nextToken());
        int last = first;
        for (int i = 1; i < n; i++) {
            if (st.hasMoreTokens()) {
                int val = Integer.parseInt(st.nextToken());
                if (i == n - 1) {
                    last = val;
                }
            }
        }
        int sum = first + last;
        if (sum % 2 == 0) {
            System.out.println("Even");
        } else {
            System.out.println("Odd");
        }
    }
}
