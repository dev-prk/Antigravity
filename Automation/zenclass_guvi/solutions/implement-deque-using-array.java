import java.util.Scanner;

public class Main {
    static class Deque {
        private int[] arr;
        private int front;
        private int rear;
        private int capacity;
        private int size;

        public Deque(int capacity) {
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

        public void insertFront(int x) {
            if (isFull()) {
                return;
            }
            if (isEmpty()) {
                front = 0;
                rear = 0;
            } else if (front == 0) {
                front = capacity - 1;
            } else {
                front--;
            }
            arr[front] = x;
            size++;
        }

        public void insertRear(int x) {
            if (isFull()) {
                return;
            }
            if (isEmpty()) {
                front = 0;
                rear = 0;
            } else if (rear == capacity - 1) {
                rear = 0;
            } else {
                rear++;
            }
            arr[rear] = x;
            size++;
        }

        public void deleteFront() {
            if (isEmpty()) {
                return;
            }
            if (front == rear) {
                front = -1;
                rear = -1;
            } else if (front == capacity - 1) {
                front = 0;
            } else {
                front++;
            }
            size--;
        }

        public void deleteRear() {
            if (isEmpty()) {
                return;
            }
            if (front == rear) {
                front = -1;
                rear = -1;
            } else if (rear == 0) {
                rear = capacity - 1;
            } else {
                rear--;
            }
            size--;
        }

        public String display() {
            StringBuilder sb = new StringBuilder();
            if (isEmpty()) {
                return sb.toString();
            }
            int i = front;
            int count = 0;
            while (count < size) {
                sb.append(arr[i]).append(" ");
                i = (i + 1) % capacity;
                count++;
            }
            return sb.toString();
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int size = sc.nextInt();
        Deque deque = new Deque(size);
        
        while (sc.hasNext()) {
            String op = sc.next();
            
            if (op.equals("exit")) {
                break;
            }
            
            if (op.equals("insertFront")) {
                int x = sc.nextInt();
                deque.insertFront(x);
            } else if (op.equals("insertRear")) {
                int x = sc.nextInt();
                deque.insertRear(x);
            } else if (op.equals("deleteFront")) {
                deque.deleteFront();
            } else if (op.equals("deleteRear")) {
                deque.deleteRear();
            } else if (op.equals("display")) {
                System.out.print(deque.display() + "\n");
            }
        }
        
        sc.close();
    }
}
