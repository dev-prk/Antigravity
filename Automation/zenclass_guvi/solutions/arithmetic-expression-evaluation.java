import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int a = sc.nextInt();
        int b = sc.nextInt();
        int c = sc.nextInt();
        int d = sc.nextInt();
        
        int sum = a + b;
        System.out.println("Sum: " + sum);
        
        int multiplication = sum * c;
        System.out.println("Multiplication Result: " + multiplication);
        
        int division = d / a;
        System.out.println("Division Result: " + division);
        
        int finalResult = multiplication + division;
        System.out.println("Final Result: " + finalResult);
        
        sc.close();
    }
}
