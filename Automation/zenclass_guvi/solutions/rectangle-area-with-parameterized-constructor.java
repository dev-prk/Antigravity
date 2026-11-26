import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int length = sc.nextInt();
        int width = sc.nextInt();
        Rectangle rect = new Rectangle(length, width);
        System.out.println(rect.getArea());
    }
}

class Rectangle {
    private int length;
    private int width;
    
    public Rectangle(int length, int width) {
        this.length = length;
        this.width = width;
    }
    
    public int getArea() {
        return length * width;
    }
}
