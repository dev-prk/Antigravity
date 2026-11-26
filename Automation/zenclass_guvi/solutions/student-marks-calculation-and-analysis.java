import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int m1 = sc.nextInt();
        int m2 = sc.nextInt();
        int m3 = sc.nextInt();
        
        int total = m1 + m2 + m3;
        int average = total / 3;
        int max = Math.max(m1, Math.max(m2, m3));
        int min = Math.min(m1, Math.min(m2, m3));
        int difference = max - min;
        int product = m1 * m2;
        
        System.out.println("Total Marks: " + total);
        System.out.println("Average Marks: " + average);
        System.out.println("Difference: " + difference);
        System.out.println("Product: " + product);
    }
}
