public class Main {
    interface QueueInterface {
        void enqueue(int x);
        int dequeue();
        int peek();
    }

    static class ArrayQueue implements QueueInterface {
        private int[] arr;
        private int front;
        private int rear;
        private int size;
        private int capacity;

        public ArrayQueue() {
            capacity = 100;
            arr = new int[capacity];
            front = 0;
            rear = 0;
            size = 0;
        }

        @Override
        public void enqueue(int x) {
            if (size == capacity) {
                resize();
            }
            arr[rear] = x;
            rear = (rear + 1) % capacity;
            size++;
        }

        private void resize() {
            int newCapacity = capacity * 2;
            int[] newArr = new int[newCapacity];
            for (int i = 0; i < size; i++) {
                newArr[i] = arr[(front + i) % capacity];
            }
            arr = newArr;
            front = 0;
            rear = size;
            capacity = newCapacity;
        }

        @Override
        public int dequeue() {
            if (size == 0) {
                return -1;
            }
            int element = arr[front];
            front = (front + 1) % capacity;
            size--;
            return element;
        }

        @Override
        public int peek() {
            if (size == 0) {
                return -1;
            }
            return arr[front];
        }
    }

    public static void main(String[] args) {
        java.util.Scanner scanner = new java.util.Scanner(System.in);
        ArrayQueue queue = new ArrayQueue();

        while (scanner.hasNextLine()) {
            String line = scanner.nextLine().trim();
            if (line.isEmpty()) {
                continue;
            }
            String[] parts = line.split(" ");
            String command = parts[0].toLowerCase();

            if (command.equals("enqueue")) {
                int x = Integer.parseInt(parts[1]);
                queue.enqueue(x);
            } else if (command.equals("dequeue")) {
                int result = queue.dequeue();
                System.out.println(result);
            } else if (command.equals("peek")) {
                int result = queue.peek();
                System.out.println(result);
            } else if (command.equals("exit")) {
                break;
            }
        }
        scanner.close();
    }
}
