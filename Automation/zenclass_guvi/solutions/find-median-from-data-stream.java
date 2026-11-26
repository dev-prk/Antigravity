import java.io.*;
import java.util.*;

public class Main {
    private PriorityQueue<Integer> maxHeap; // lower half
    private PriorityQueue<Integer> minHeap; // upper half
    
    public Main() {
        maxHeap = new PriorityQueue<>(Collections.reverseOrder());
        minHeap = new PriorityQueue<>();
    }
    
    public void addNum(int num) {
        if (maxHeap.isEmpty() || num <= maxHeap.peek()) {
            maxHeap.offer(num);
        } else {
            minHeap.offer(num);
        }
        
        // Balance the heaps
        if (maxHeap.size() > minHeap.size() + 1) {
            minHeap.offer(maxHeap.poll());
        } else if (minHeap.size() > maxHeap.size()) {
            maxHeap.offer(minHeap.poll());
        }
    }
    
    public double findMedian() {
        if (maxHeap.size() == minHeap.size()) {
            return (maxHeap.peek() + minHeap.peek()) / 2.0;
        } else {
            return maxHeap.peek();
        }
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        Main solution = new Main();
        
        int n = Integer.parseInt(br.readLine().trim());
        
        for (int i = 0; i < n; i++) {
            String line = br.readLine().trim();
            String[] parts = line.split("\\s+");
            
            if (parts[0].equals("addNum")) {
                int num = Integer.parseInt(parts[1]);
                solution.addNum(num);
            } else if (parts[0].equals("findMedian")) {
                double median = solution.findMedian();
                System.out.printf("%.1f%n", median);
            }
        }
    }
}
