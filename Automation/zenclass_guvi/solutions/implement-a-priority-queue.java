import java.io.*;
import java.util.*;

public class Main {
    static class Node {
        int value;
        int priority;
        int index;
        
        Node(int value, int priority, int index) {
            this.value = value;
            this.priority = priority;
            this.index = index;
        }
    }
    
    static class PriorityQueue {
        private List<Node> heap = new ArrayList<>();
        private int indexCounter = 0;
        
        public void enqueue(int value, int priority) {
            Node node = new Node(value, priority, indexCounter++);
            heap.add(node);
            int current = heap.size() - 1;
            while (current > 0) {
                int parent = (current - 1) / 2;
                Node currentNode = heap.get(current);
                Node parentNode = heap.get(parent);
                if (currentNode.priority > parentNode.priority || 
                    (currentNode.priority == parentNode.priority && currentNode.index < parentNode.index)) {
                    Collections.swap(heap, current, parent);
                    current = parent;
                } else {
                    break;
                }
            }
        }
        
        public int peek() {
            if (heap.isEmpty()) return -1;
            return heap.get(0).value;
        }
        
        public int dequeue() {
            if (heap.isEmpty()) return -1;
            Node result = heap.get(0);
            Node last = heap.remove(heap.size() - 1);
            if (!heap.isEmpty()) {
                heap.set(0, last);
                heapify(0);
            }
            return result.value;
        }
        
        private void heapify(int index) {
            int smallest = index;
            int left = 2 * index + 1;
            int right = 2 * index + 2;
            
            if (left < heap.size()) {
                Node leftNode = heap.get(left);
                Node smallestNode = heap.get(smallest);
                if (leftNode.priority > smallestNode.priority || 
                    (leftNode.priority == smallestNode.priority && leftNode.index < smallestNode.index)) {
                    smallest = left;
                }
            }
            
            if (right < heap.size()) {
                Node rightNode = heap.get(right);
                Node smallestNode = heap.get(smallest);
                if (rightNode.priority > smallestNode.priority || 
                    (rightNode.priority == smallestNode.priority && rightNode.index < smallestNode.index)) {
                    smallest = right;
                }
            }
            
            if (smallest != index) {
                Collections.swap(heap, index, smallest);
                heapify(smallest);
            }
        }
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        PriorityQueue pq = new PriorityQueue();
        int n = Integer.parseInt(br.readLine().trim());
        
        StringBuilder sb = new StringBuilder();
        
        for (int i = 0; i < n; i++) {
            String line = br.readLine().trim();
            String[] parts = line.split(" ");
            
            if (parts[0].equals("ENQUEUE")) {
                int value = Integer.parseInt(parts[1]);
                int priority = Integer.parseInt(parts[2]);
                pq.enqueue(value, priority);
            } else if (parts[0].equals("DEQUEUE")) {
                int val = pq.dequeue();
                sb.append(val).append("\n");
            } else if (parts[0].equals("PEEK")) {
                int val = pq.peek();
                sb.append(val).append("\n");
            }
        }
        
        System.out.print(sb.toString());
    }
}
