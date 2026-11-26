import java.util.ArrayList;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        GenericStack<String> stack = new GenericStack<>();
        
        int n = Integer.parseInt(sc.nextLine());
        
        for (int i = 0; i < n; i++) {
            String line = sc.nextLine();
            String[] parts = line.split(" ", 2);
            String command = parts[0];
            
            if (command.equals("push")) {
                String value = parts[1];
                stack.push(value);
                System.out.println("Pushed: " + value);
            } else if (command.equals("pop")) {
                String result = stack.pop();
                System.out.println("Popped: " + result);
            } else if (command.equals("peek")) {
                String result = stack.peek();
                System.out.println("Peek: " + result);
            }
        }
        
        sc.close();
    }
}

class GenericStack<T> {
    private ArrayList<T> list;
    
    public GenericStack() {
        list = new ArrayList<>();
    }
    
    public void push(T item) {
        list.add(item);
    }
    
    public T pop() {
        if (list.isEmpty()) {
            return null;
        }
        return list.remove(list.size() - 1);
    }
    
    public T peek() {
        if (list.isEmpty()) {
            return null;
        }
        return list.get(list.size() - 1);
    }
}
