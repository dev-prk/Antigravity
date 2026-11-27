import java.util.Scanner;

class Shape {
    public double area() {
        return 0.0;
    }
}

class Rectangle extends Shape {
    private int length;
    private int breadth;

    public Rectangle(int length, int breadth) {
        this.length = length;
        this.breadth = breadth;
    }

    @Override
    public double area() {
        return (double) ((long) length * breadth);
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int length = scanner.nextInt();
        int breadth = scanner.nextInt();
        scanner.close();

        Rectangle rectangle = new Rectangle(length, breadth);
        double area = rectangle.area();

        if (area == Math.floor(area) && !Double.isInfinite(area)) {
            System.out.println((long) area);
        } else {
            System.out.println(area);
        }
    }
}
