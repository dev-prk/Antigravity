import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] first = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(first[0]);
        int min = 0;
        if (n > 0) {
            String[] nums = br.readLine().trim().split("\\s+");
            min = Integer.parseInt(nums[0]);
            for (int i = 1; i < n; i++) {
                int val = Integer.parseInt(nums[i]);
                if (val < min) min = val;
            }
        }
        System.out.println(min);
    }
}
