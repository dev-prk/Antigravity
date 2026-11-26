import java.util.Scanner;

class Pair<T, U> {
    private T first;
    private U second;

    public Pair() {
    }

    public Pair(T first, U second) {
        this.first = first;
        this.second = second;
    }

    public void setFirst(T first) {
        this.first = first;
    }

    public void setSecond(U second) {
        this.second = second;
    }

    public T getFirst() {
        return first;
    }

    public U getSecond() {
        return second;
    }

    public void swap() {
        T temp = first;
        first = (T) second;
        second = (U) temp;
    }

    public String toString() {
        return "(" + first + ", " + second + ")";
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        String type1 = sc.nextLine().trim();
        Object first = null;
        if (type1.equals("Integer")) {
            first = Integer.parseInt(sc.nextLine().trim());
        } else {
            first = sc.nextLine().trim();
        }
        
        String type2 = sc.nextLine().trim();
        Object second = null;
        if (type2.equals("Integer")) {
            second = Integer.parseInt(sc.nextLine().trim());
        } else {
            second = sc.nextLine().trim();
        }
        
        Pair<Object, Object> pair = new Pair<>(first, second);
        
        System.out.println("Original Pair: " + pair.toString());
        pair.swap();
        System.out.println("Swapped Pair: " + pair.toString());
        
        sc.close();
    }
}
