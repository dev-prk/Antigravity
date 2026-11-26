import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        String input = scanner.nextLine();
        
        if (input == null || input.trim().isEmpty()) {
            System.out.println(0);
            System.out.println("0 0");
            System.out.println("0.00");
            return;
        }
        
        String[] parts = input.trim().split("\\s+");
        
        int[] numbers = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            numbers[i] = Integer.valueOf(parts[i]);
        }
        
        int sum = 0;
        for (int num : numbers) {
            sum += num;
        }
        
        int max = numbers[0];
        int min = numbers[0];
        for (int num : numbers) {
            if (num > max) {
                max = num;
            }
            if (num < min) {
                min = num;
            }
        }
        
        double average = (double) sum / numbers.length;
        
        System.out.println(sum);
        System.out.println(max + " " + min);
        System.out.printf("%.2f%n", average);
    }
}
