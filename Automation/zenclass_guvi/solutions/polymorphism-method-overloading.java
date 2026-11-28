import java.util.Scanner;

public class Main {
    // Method overloading - three different calculate methods
    public static int calculate(int a, int b) {
        return a + b;
    }
    
    public static double calculate(double a, double b) {
        return a + b;
    }
    
    public static String calculate(String a, String b) {
        return a + b;
    }
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        String dataType = sc.nextLine();
        int choice = 0;
        
        switch(dataType) {
            case "int":
                choice = 1;
                break;
            case "float":
                choice = 2;
                break;
            case "string":
                choice = 3;
                break;
        }
        
        String val1 = sc.nextLine();
        String val2 = sc.nextLine();
        
        switch(choice) {
            case 1:
                int a = Integer.parseInt(val1);
                int b = Integer.parseInt(val2);
                System.out.println(calculate(a, b));
                break;
            case 2:
                double c = Double.parseDouble(val1);
                double d = Double.parseDouble(val2);
                double result = calculate(c, d);
                // Check if result is an integer (whole number)
                if (result == Math.floor(result) && !Double.isInfinite(result)) {
                    System.out.println((int) result);
                } else {
                    System.out.println(result);
                }
                break;
            case 3:
                System.out.println(calculate(val1, val2));
                break;
        }
        
        sc.close();
    }
}
