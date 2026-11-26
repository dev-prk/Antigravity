import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

interface AddToCart {
    void addItem(String item);
}

interface Payment {
    void makePayment();
}

class ShoppingCart implements AddToCart, Payment {
    private final List<String> items = new ArrayList<>();

    @Override
    public void addItem(String item) {
        items.add(item);
        System.out.println("Item added: " + item);
    }

    @Override
    public void makePayment() {
        System.out.println("Payment successful for " + items.size() + " items.");
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        ShoppingCart cart = new ShoppingCart();

        while (scanner.hasNextLine()) {
            String line = scanner.nextLine().trim();
            if (line.isEmpty()) {
                continue;
            }

            String lower = line.toLowerCase();

            if (lower.equals("pay")) {
                cart.makePayment();
                break;
            }

            if (lower.startsWith("add ") && line.length() > 4) {
                String item = line.substring(4).trim();
                if (!item.isEmpty()) {
                    cart.addItem(item);
                }
            }
        }

        scanner.close();
    }
}
