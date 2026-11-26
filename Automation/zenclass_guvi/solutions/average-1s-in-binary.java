import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int N = sc.nextInt();
        int[] arr = new int[N];
        
        for (int i = 0; i < N; i++) {
            arr[i] = sc.nextInt();
        }
        
        int totalOnes = 0;
        
        for (int num : arr) {
            String binary = Integer.toBinaryString(num);
            int count = 0;
            for (char c : binary.toCharArray()) {
                if (c == '1') {
                    count++;
                }
            }
            totalOnes += count;
        }
        
        double average = (double) totalOnes / N;
        int result = (int) Math.round(average);
        
        System.out.println(result);
    }
}
