import java.util.*;
import java.io.*;

class Product {
    double price;
    int discount;
    
    public Product(double price, int discount) {
        this.price = price;
        this.discount = discount;
    }
    
    public double getPrice() {
        return price;
    }
    
    public int getDiscount() {
        return discount;
    }
}

class SpecialProduct extends Product {
    final int maxDiscount;
    
    public SpecialProduct(double price, int discount, int maxDiscount) {
        super(price, discount);
        this.maxDiscount = maxDiscount;
    }
    
    public int getAppliedDiscount() {
        if (getPrice() <= 0 || getDiscount() <= 0) {
            return 0;
        }
        int discount = getDiscount();
        if (discount > maxDiscount) {
            discount = maxDiscount;
        }
        if (discount > getPrice()) {
            discount = (int)getPrice();
        }
        return discount;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        if (!sc.hasNextDouble()) {
            System.out.println("Applied Discount: 0");
            return;
        }
        
        double price = sc.nextDouble();
        
        if (!sc.hasNextInt()) {
            System.out.println("Applied Discount: 0");
            return;
        }
        
        int discount = sc.nextInt();
        
        SpecialProduct sp = new SpecialProduct(price, discount, 500);
        int appliedDiscount = sp.getAppliedDiscount();
        
        System.out.println("Applied Discount: " + appliedDiscount);
    }
}
