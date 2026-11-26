import java.util.Scanner;

class Rectangle {
    private int width;
    private int height;

    // Constructor with no arguments
    public Rectangle() {
        this.width = 0;
        this.height = 0;
    }

    // Constructor with one argument (square)
    public Rectangle(int side) {
        this.width = side;
        this.height = side;
    }

    // Constructor with two arguments (rectangle)
    public Rectangle(int width, int height) {
        this.width = width;
        this.height = height;
    }

    // Method to calculate area
    public int calculateArea() {
        return this.width * this.height;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        int width = scanner.nextInt();
        int height = scanner.nextInt();
        
        Rectangle rect = new Rectangle(width, height);
        
        System.out.println(rect.calculateArea());
        
        scanner.close();
    }
}
