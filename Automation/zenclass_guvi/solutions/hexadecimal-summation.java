import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        if (!sc.hasNextInt()) {
            sc.close();
            return;
        }
        
        int n = sc.nextInt();
        sc.nextLine();
        
        if (n <= 0) {
            System.out.println("0");
            sc.close();
            return;
        }
        
        String line = sc.nextLine();
        String[] parts = line.trim().split("\\s+");
        
        long sum = 0;
        for (int i = 0; i < n && i < parts.length; i++) {
            String hex = parts[i].trim();
            if (!hex.isEmpty()) {
                sum += Integer.parseInt(hex, 16);
            }
        }
        
        System.out.println(Integer.toHexString((int)sum));
        
        sc.close();
    }
}
