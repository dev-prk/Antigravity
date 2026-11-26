import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        Rectangle rect = new Rectangle(a, b);
        System.out.println(rect.getArea());
    }
}

class Rectangle {
    private int width;
    private int height;

    public Rectangle() {
        this.width = 0;
        this.height = 0;
    }

    public Rectangle(int side) {
        this.width = side;
        this.height = side;
    }

    public Rectangle(int a, int b) {
        if (b == -1) {
            this.width = a;
            this.height = a;
        } else {
            this.width = a;
            this.height = b;
        }
    }

    public int getArea() {
        return width * height;
    }
}
