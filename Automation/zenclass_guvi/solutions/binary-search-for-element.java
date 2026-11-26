import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null || line.trim().isEmpty()) {
            return;
        }
        int n = Integer.parseInt(line.trim());
        int[] arr = new int[n];
        if (n > 0) {
            // Read until we have n integers
            int count = 0;
            while (count < n) {
                String line2 = br.readLine();
                if (line2 == null) break;
                StringTokenizer st = new StringTokenizer(line2);
                while (st.hasMoreTokens() && count < n) {
                    arr[count++] = Integer.parseInt(st.nextToken());
                }
            }
        }
        String lineX = br.readLine();
        if (lineX == null) {
            System.out.println(-1);
            return;
        }
        int target = Integer.parseInt(lineX.trim());

        int left = 0, right = n - 1;
        int ans = -1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) {
                ans = mid;
                break;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        System.out.println(ans);
    }
}
