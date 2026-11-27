import java.util.*;
import java.util.stream.Collectors;

// Generic Sorter class that uses Comparator<T>
class Sorter<T> {
    public void sort(T[] array, Comparator<T> comparator) {
        Arrays.sort(array, comparator);
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        // Read the type
        String type = sc.nextLine().trim();
        
        // Read the elements line
        String elementsLine = sc.nextLine().trim();
        
        if (type.equalsIgnoreCase("Integer")) {
            // Parse integers
            String[] parts = elementsLine.split("\\s+");
            Integer[] arr = new Integer[parts.length];
            for (int i = 0; i < parts.length; i++) {
                arr[i] = Integer.parseInt(parts[i]);
            }
            
            // Sort using Sorter
            Sorter<Integer> sorter = new Sorter<>();
            sorter.sort(arr, Integer::compareTo);
            
            // Print the result
            System.out.println("Sorted Integer Array: " + Arrays.toString(arr));
        } else if (type.equalsIgnoreCase("String")) {
            // Parse strings
            String[] parts = elementsLine.split("\\s+");
            String[] arr = parts;
            
            // Sort using Sorter
            Sorter<String> sorter = new Sorter<>();
            sorter.sort(arr, String::compareTo);
            
            // Print the result
            System.out.println("Sorted String Array: " + Arrays.toString(arr));
        }
        
        sc.close();
    }
}
