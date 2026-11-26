import java.util.*;
import java.io.*;

class Item {
    static double totalDiscount = 0;
    
    double price;
    double discountPercent;
    
    Item(double price, double discountPercent) {
        this.price = price;
        this.discountPercent = discountPercent;
    }
    
    void applyDiscount() {
        totalDiscount += price * discountPercent / 100.0;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        while (sc.hasNextDouble()) {
            double price = sc.nextDouble();
            double discount = sc.nextDouble();
            Item item = new Item(price, discount);
            item.applyDiscount();
        }
        
        sc.close();
        
        System.out.printf("Total Discount: %.0f\n", Item.totalDiscount);
    }
}
