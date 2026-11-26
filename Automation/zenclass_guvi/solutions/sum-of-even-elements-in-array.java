import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String nLine = br.readLine();
        if (nLine == null || nLine.isEmpty()) {
            System.out.println(0);
            return;
        }
        int n = Integer.parseInt(nLine.trim());
        if (n <= 0) {
            System.out.println(0);
            return;
        }
        String arrLine = br.readLine();
        if (arrLine == null || arrLine.isEmpty()) {
            System.out.println(0);
            return;
        }
        StringTokenizer st = new StringTokenizer(arrLine);
        long sum = 0;
        int count = 0;
        while (st.hasMoreTokens() && count < n) {
            int num = Integer.parseInt(st.nextToken());
            if (num % 2 == 0) {
                sum += num;
            }
            count++;
        }
        System.out.println(sum);
    }
}
