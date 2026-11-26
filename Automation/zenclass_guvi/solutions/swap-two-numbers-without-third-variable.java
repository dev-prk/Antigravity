public class Main {
    public static void main(String[] args) {
        java.util.Scanner scanner = new java.util.Scanner(System.in);
        
        int a = scanner.nextInt();
        int b = scanner.nextInt();
        
        System.out.println("Before swap: " + a + " " + b);
        
        a = a + b;
        b = a - b;
        a = a - b;
        
        System.out.println("After swap: " + a + " " + b);
        
        scanner.close();
    }
}
