import java.util.Scanner;

public class Main {
    public static void main(String[] args) throws InterruptedException {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        int t = sc.nextInt();
        
        int totalSegments = (int) Math.ceil((double) n / t);
        Thread[] threads = new Thread[t];
        final int[] totalSum = {0};
        
        for (int i = 0; i < t; i++) {
            final int start = i * totalSegments;
            final int end = Math.min(start + totalSegments, n);
            
            threads[i] = new Thread(() -> {
                int sum = 0;
                for (int j = start; j < end; j++) {
                    sum += arr[j];
                }
                synchronized (totalSum) {
                    totalSum[0] += sum;
                }
            });
            
            threads[i].start();
        }
        
        for (Thread thread : threads) {
            thread.join();
        }
        
        System.out.println("Total Sum: " + totalSum[0]);
    }
}
