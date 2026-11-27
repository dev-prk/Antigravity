import java.util.*;
import java.util.stream.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        if (!sc.hasNextInt()) {
            sc.close();
            return;
        }
        
        int n = sc.nextInt();
        sc.nextLine(); // consume newline
        
        if (n <= 0) {
            System.out.println("Maximum: -1");
            sc.close();
            return;
        }
        
        String line = sc.nextLine().trim();
        sc.close();
        
        if (line.isEmpty()) {
            System.out.println("Maximum: -1");
            return;
        }
        
        String[] tokens = line.split("\\s+");
        
        // Try to determine if all are integers
        boolean allIntegers = true;
        boolean allDoubles = true;
        List<Integer> intList = new ArrayList<>();
        List<Double> doubleList = new ArrayList<>();
        List<String> stringList = new ArrayList<>();
        
        for (String token : tokens) {
            if (token.isEmpty()) continue;
            
            try {
                int val = Integer.parseInt(token);
                intList.add(val);
            } catch (NumberFormatException e) {
                allIntegers = false;
                break;
            }
        }
        
        if (allIntegers && !intList.isEmpty()) {
            Collections.sort(intList);
            System.out.println("Maximum: " + intList.get(intList.size() - 1));
            return;
        }
        
        // Try doubles
        Collections.sort(doubleList);
        for (String token : tokens) {
            if (token.isEmpty()) continue;
            
            try {
                double val = Double.parseDouble(token);
                doubleList.add(val);
            } catch (NumberFormatException e) {
                allDoubles = false;
                break;
            }
        }
        
        if (allDoubles && !doubleList.isEmpty()) {
            Collections.sort(doubleList);
            System.out.println("Maximum: " + doubleList.get(doubleList.size() - 1));
            return;
        }
        
        // Default to strings
        for (String token : tokens) {
            if (!token.isEmpty()) {
                stringList.add(token);
            }
        }
        
        if (stringList.isEmpty()) {
            System.out.println("Maximum: -1");
            return;
        }
        
        Collections.sort(stringList);
        System.out.println("Maximum: " + stringList.get(stringList.size() - 1));
    }
}
