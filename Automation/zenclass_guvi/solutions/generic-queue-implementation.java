import java.util.LinkedList;
import java.util.Scanner;

class Queue<T> {
    private LinkedList<T> data;
    
    public Queue() {
        data = new LinkedList<>();
    }
    
    public void enqueue(T item) {
        data.addLast(item);
    }
    
    public T dequeue() {
        if (isEmpty()) {
            return null;
        }
        return data.removeFirst();
    }
    
    public T peek() {
        if (isEmpty()) {
            return null;
        }
        return data.getFirst();
    }
    
    public boolean isEmpty() {
        return data.isEmpty();
    }
    
    public void print() {
        System.out.print("Queue contents: [");
        for (int i = 0; i < data.size(); i++) {
            System.out.print(data.get(i));
            if (i < data.size() - 1) {
                System.out.print(", ");
            }
        }
        System.out.println("]");
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Queue<Object> queue = new Queue<>();
        
        while (scanner.hasNextLine()) {
            String line = scanner.nextLine().trim();
            if (line.isEmpty()) {
                continue;
            }
            
            String[] parts = line.split(" ", 2);
            String command = parts[0].toLowerCase();
            
            if (command.equals("enqueue")) {
                if (parts.length > 1) {
                    queue.enqueue(parts[1]);
                }
            } else if (command.equals("dequeue")) {
                Object val = queue.dequeue();
                if (val != null) {
                    System.out.println("Dequeued value: " + val);
                }
            } else if (command.equals("peek")) {
                Object val = queue.peek();
                if (val != null) {
                    System.out.println("Front of the queue: " + val);
                }
            } else if (command.equals("print")) {
                queue.print();
            } else if (command.equals("exit")) {
                break;
            }
        }
        
        scanner.close();
    }
}
