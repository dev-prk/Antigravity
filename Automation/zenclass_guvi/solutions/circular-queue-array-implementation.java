import java.io.*;
import java.util.*;

public class Main {
    static class CircularQueue {
        private int[] arr;
        private int front;
        private int rear;
        private int size;
        private int capacity;

        public CircularQueue(int capacity) {
            this.capacity = capacity;
            arr = new int[capacity];
            front = -1;
            rear = -1;
            size = 0;
        }

        public boolean isFull() {
            return size == capacity;
        }

        public boolean isEmpty() {
            return size == 0;
        }

        public void enqueue(int value) {
            if (isFull()) {
                return;
            }
            if (isEmpty()) {
                front = 0;
            }
            rear = (rear + 1) % capacity;
            arr[rear] = value;
            size++;
        }

        public void dequeue() {
            if (isEmpty()) {
                return;
            }
            if (front == rear) {
                front = -1;
                rear = -1;
            } else {
                front = (front + 1) % capacity;
            }
            size--;
        }

        public void display() {
            if (isEmpty()) {
                System.out.println();
                return;
            }
            StringBuilder sb = new StringBuilder();
            int count = size;
            int index = front;
            while (count > 0) {
                sb.append(arr[index]).append(" ");
                index = (index + 1) % capacity;
                count--;
            }
            System.out.println(sb.toString());
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int capacity = sc.nextInt();
        CircularQueue cq = new CircularQueue(capacity);
        
        while (sc.hasNext()) {
            String command = sc.next();
            if (command.equals("exit")) {
                break;
            }
            if (command.equals("enqueue")) {
                int value = sc.nextInt();
                cq.enqueue(value);
            } else if (command.equals("dequeue")) {
                cq.dequeue();
            } else if (command.equals("display")) {
                cq.display();
            }
        }
        sc.close();
    }
}
