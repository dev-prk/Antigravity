import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int start = sc.nextInt();
        int end = sc.nextInt();
        int threads = sc.nextInt();
        
        sc.close();
        
        if (start > end || threads <= 0) {
            System.out.println("Primes: []");
            return;
        }
        
        List<Integer> allPrimes = Collections.synchronizedList(new ArrayList<>());
        
        threads = Math.max(1, Math.min(threads, end - start + 1));
        
        ExecutorService executor = Executors.newFixedThreadPool(threads);
        
        int rangeSize = end - start + 1;
        int segmentSize = (rangeSize + threads - 1) / threads;
        
        List<Future<List<Integer>>> futures = new ArrayList<>();
        
        for (int i = 0; i < threads; i++) {
            int segStart = start + i * segmentSize;
            int segEnd = Math.min(segStart + segmentSize - 1, end);
            
            if (segStart > segEnd) break;
            
            futures.add(executor.submit(new PrimeTask(segStart, segEnd)));
        }
        
        executor.shutdown();
        
        for (Future<List<Integer>> future : futures) {
            try {
                allPrimes.addAll(future.get());
            } catch (Exception e) {
                // Handle exception
            }
        }
        
        Collections.sort(allPrimes);
        
        System.out.print("Primes: [");
        for (int i = 0; i < allPrimes.size(); i++) {
            if (i > 0) System.out.print(", ");
            System.out.print(allPrimes.get(i));
        }
        System.out.println("]");
    }
    
    static class PrimeTask implements Callable<List<Integer>> {
        private final int start;
        private final int end;
        
        public PrimeTask(int start, int end) {
            this.start = start;
            this.end = end;
        }
        
        @Override
        public List<Integer> call() {
            List<Integer> primes = new ArrayList<>();
            
            for (int num = start; num <= end; num++) {
                if (isPrime(num)) {
                    primes.add(num);
                }
            }
            
            return primes;
        }
        
        private boolean isPrime(int n) {
            if (n < 2) return false;
            if (n == 2) return true;
            if (n % 2 == 0) return false;
            
            for (int i = 3; i * i <= n; i += 2) {
                if (n % i == 0) return false;
            }
            
            return true;
        }
    }
}
