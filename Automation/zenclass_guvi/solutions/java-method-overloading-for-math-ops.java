import java.util.*;
import java.util.stream.*;

public class Main {
    // Integer operations
    public static int add(int a, int b) { return a + b; }
    public static int subtract(int a, int b) { return a - b; }
    public static int multiply(int a, int b) { return a * b; }
    public static int divide(int a, int b) { return b != 0 ? a / b : -1; }
    public static int add(int... nums) { return Arrays.stream(nums).sum(); }
    
    // Float operations
    public static double add(double a, double b) { return a + b; }
    public static double subtract(double a, double b) { return a - b; }
    public static double multiply(double a, double b) { return a * b; }
    public static double divide(double a, double b) { return b != 0 ? a / b : -1; }
    public static double add(double... nums) { return Arrays.stream(nums).sum(); }
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String op = sc.next();
        String type = sc.next();
        double a = sc.nextDouble();
        double b = sc.nextDouble();
        
        sc.close();
        
        switch(op) {
            case "Addition":
                if(type.equals("int")) {
                    int sum = add((int)a, (int)b);
                    System.out.println("Sum of " + (int)a + " and " + (int)b + " is: " + sum);
                } else {
                    double sum = add(a, b);
                    System.out.println("Sum of " + a + " and " + b + " is: " + sum);
                }
                break;
            case "Subtraction":
                if(type.equals("int")) {
                    int diff = subtract((int)a, (int)b);
                    System.out.println("Difference of " + (int)a + " and " + (int)b + " is: " + diff);
                } else {
                    double diff = subtract(a, b);
                    System.out.println("Difference of " + a + " and " + b + " is: " + diff);
                }
                break;
            case "Multiplication":
                if(type.equals("int")) {
                    int prod = multiply((int)a, (int)b);
                    System.out.println("Product of " + (int)a + " and " + (int)b + " is: " + prod);
                } else {
                    double prod = multiply(a, b);
                    System.out.println("Product of " + a + " and " + b + " is: " + prod);
                }
                break;
            case "Division":
                if(type.equals("int")) {
                    int quot = divide((int)a, (int)b);
                    System.out.println("Quotient of " + (int)a + " and " + (int)b + " is: " + quot);
                } else {
                    double quot = divide(a, b);
                    System.out.println("Quotient of " + a + " and " + b + " is: " + quot);
                }
                break;
        }
    }
}
