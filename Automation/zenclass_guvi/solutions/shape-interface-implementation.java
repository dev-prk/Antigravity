import java.util.Scanner;

interface Shape {
    double area();
    double perimeter();
}

class Rectangle implements Shape {
    private double length;
    private double width;

    public Rectangle(double length, double width) {
        this.length = length;
        this.width = width;
    }

    @Override
    public double area() {
        return length * width;
    }

    @Override
    public double perimeter() {
        return 2 * (length + width);
    }
}

class Circle implements Shape {
    private double radius;

    public Circle(double radius) {
        this.radius = radius;
    }

    @Override
    public double area() {
        return Math.PI * radius * radius;
    }

    @Override
    public double perimeter() {
        return 2 * Math.PI * radius;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String shapeType = scanner.next();
        
        Shape shape;
        if (shapeType.equalsIgnoreCase("Rectangle")) {
            double length = scanner.nextDouble();
            double width = scanner.nextDouble();
            shape = new Rectangle(length, width);
        } else if (shapeType.equalsIgnoreCase("Circle")) {
            double radius = scanner.nextDouble();
            shape = new Circle(radius);
        } else {
            return;
        }
        
        System.out.println("Area: " + shape.area());
        System.out.println("Perimeter: " + shape.perimeter());
    }
}
