import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] tokens = br.readLine().trim().split("\\s+");
        
        long oddSum = 0, evenSum = 0;
        for (String t : tokens) {
            int x = Integer.parseInt(t);
            if (x == -1) break;
            if (x % 2 == 0) {
                evenSum += x;
            } else {
                oddSum += x;
            }
        }
        
        if (oddSum > evenSum) {
            System.out.println("Odd Sum Greater");
        } else {
            System.out.println("Even Sum Greater");
        }
    }
}
