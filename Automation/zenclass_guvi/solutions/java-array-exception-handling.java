import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        int n = scanner.nextInt();
        int[] arr = new int[n];
        
        for (int i = 0; i < n; i++) {
            arr[i] = scanner.nextInt();
        }
        
        int index = scanner.nextInt();
        
        try {
            int element = arr[index];
            System.out.println("Element at index " + index + ": " + element);
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("ArrayIndexOutOfBoundsException: Index " + index + " out of bounds for length " + n);
        }
    }
}
