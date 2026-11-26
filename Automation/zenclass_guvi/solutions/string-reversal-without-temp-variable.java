import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null || s.length() == 0) {
            System.out.println("");
            return;
        }
        char[] arr = s.toCharArray();
        int n = arr.length;
        for (int i = 0; i < n / 2; i++) {
            arr[i] ^= arr[n - 1 - i];
            arr[n - 1 - i] ^= arr[i];
            arr[i] ^= arr[n - 1 - i];
        }
        System.out.println(new String(arr));
    }
}
