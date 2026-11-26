import java.util.concurrent.atomic.AtomicInteger;

public class Main {
    public static void main(String[] args) throws InterruptedException {
        java.util.Scanner scanner = new java.util.Scanner(System.in);
        
        int n = scanner.nextInt();
        int m = scanner.nextInt();
        
        Counter counter = new Counter();
        Thread[] threads = new Thread[n];
        
        for (int i = 0; i < n; i++) {
            final int incrementsPerThread = m;
            threads[i] = new Thread(() -> {
                for (int j = 0; j < incrementsPerThread; j++) {
                    counter.increment();
                }
            });
        }
        
        for (Thread thread : threads) {
            thread.start();
        }
        
        for (Thread thread : threads) {
            thread.join();
        }
        
        System.out.println("Final Counter: " + counter.getValue());
        scanner.close();
    }
    
    static class Counter {
        private final AtomicInteger value = new AtomicInteger(0);
        
        public synchronized void increment() {
            value.addAndGet(1);
        }
        
        public int getValue() {
            return value.get();
        }
    }
}
