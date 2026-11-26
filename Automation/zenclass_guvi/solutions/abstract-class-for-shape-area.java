import java.util.Scanner;

abstract class Shape {
    abstract double calculateArea();
}

class Circle extends Shape {
    private double radius;
    
    public Circle(double radius) {
        this.radius = radius;
    }
    
    @Override
    double calculateArea() {
        return Math.PI * radius * radius;
    }
}

class Rectangle extends Shape {
    private double length;
    private double width;
    
    public Rectangle(double length, double width) {
        this.length = length;
        this.width = width;
    }
    
    @Override
    double calculateArea() {
        return length * width;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        String shapeType = sc.nextLine().trim();
        
        Shape shape;
        if (shapeType.equalsIgnoreCase("circle")) {
            double radius = sc.nextDouble();
            shape = new Circle(radius);
        } else {
            double length = sc.nextDouble();
            double width = sc.nextDouble();
            shape = new Rectangle(length, width);
        }
        
        System.out.printf("%.2f%n", shape.calculateArea());
    }
}
