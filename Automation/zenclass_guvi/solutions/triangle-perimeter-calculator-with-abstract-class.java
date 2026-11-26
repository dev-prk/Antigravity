import java.util.*;
import java.io.*;

abstract class Shape {
    abstract double perimeter();
}

class Triangle extends Shape {
    private double side1, side2, side3;
    
    public Triangle(double side1, double side2, double side3) {
        this.side1 = side1;
        this.side2 = side2;
        this.side3 = side3;
    }
    
    @Override
    double perimeter() {
        return side1 + side2 + side3;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String type = sc.next();
        double a = sc.nextDouble();
        double b = sc.nextDouble();
        double c = sc.nextDouble();
        sc.close();
        
        Shape s = new Triangle(a, b, c);
        System.out.println("Perimeter: " + (int)s.perimeter());
    }
}
