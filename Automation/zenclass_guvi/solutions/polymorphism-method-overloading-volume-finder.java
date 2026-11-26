import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        String shape = sc.nextLine().trim();
        
        double volume;
        
        if (shape.equals("cube")) {
            double side = sc.nextDouble();
            volume = findVolume(side);
        } else if (shape.equals("cuboid")) {
            double length = sc.nextDouble();
            double breadth = sc.nextDouble();
            double height = sc.nextDouble();
            volume = findVolume(length, breadth, height);
        } else if (shape.equals("cylinder")) {
            double radius = sc.nextDouble();
            double height = sc.nextDouble();
            volume = findVolume(radius, height, true);
        } else {
            volume = 0;
        }
        
        System.out.printf("%.2f%n", volume);
        sc.close();
    }
    
    public static double findVolume(double side) {
        return side * side * side;
    }
    
    public static double findVolume(double length, double breadth, double height) {
        return length * breadth * height;
    }
    
    public static double findVolume(double radius, double height, boolean isCylinder) {
        return Math.PI * radius * radius * height;
    }
}
