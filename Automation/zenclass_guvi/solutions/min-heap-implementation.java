import java.io.*;
import java.util.*;

public class Main {
    static class MinHeap {
        private List<Integer> heap;

        public MinHeap() {
            heap = new ArrayList<>();
        }

        public void insert(int val) {
            heap.add(val);
            siftUp(heap.size() - 1);
        }

        public int extractMin() {
            if (heap.isEmpty()) return -1;
            
            int minVal = heap.get(0);
            int lastVal = heap.remove(heap.size() - 1);
            
            if (!heap.isEmpty()) {
                heap.set(0, lastVal);
                siftDown(0);
            }
            
            return minVal;
        }

        public void heapify(int[] arr) {
            heap.clear();
            for (int val : arr) {
                heap.add(val);
            }
            
            for (int i = heap.size() / 2 - 1; i >= 0; i--) {
                siftDown(i);
            }
        }

        private void siftUp(int idx) {
            while (idx > 0) {
                int parentIdx = (idx - 1) / 2;
                if (heap.get(idx) >= heap.get(parentIdx)) break;
                
                Collections.swap(heap, idx, parentIdx);
                idx = parentIdx;
            }
        }

        private void siftDown(int idx) {
            int size = heap.size();
            
            while (true) {
                int smallest = idx;
                int left = 2 * idx + 1;
                int right = 2 * idx + 2;

                if (left < size && heap.get(left) < heap.get(smallest)) {
                    smallest = left;
                }

                if (right < size && heap.get(right) < heap.get(smallest)) {
                    smallest = right;
                }

                if (smallest == idx) break;

                Collections.swap(heap, idx, smallest);
                idx = smallest;
            }
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        MinHeap heap = new MinHeap();
        
        int n = Integer.parseInt(br.readLine().trim());
        
        for (int i = 0; i < n; i++) {
            String line = br.readLine().trim();
            String[] parts = line.split("\\s+");
            
            if (parts[0].equals("insert")) {
                int val = Integer.parseInt(parts[1]);
                heap.insert(val);
            } else if (parts[0].equals("extractMin")) {
                int min = heap.extractMin();
                System.out.println(min);
            } else if (parts[0].equals("heapify")) {
                int k = Integer.parseInt(parts[1]);
                int[] arr = new int[k];
                for (int j = 0; j < k; j++) {
                    arr[j] = Integer.parseInt(parts[2 + j]);
                }
                heap.heapify(arr);
            }
        }
    }
}
