import java.util.Scanner;
import java.util.Arrays;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        String s1 = scanner.nextLine();
        String s2 = scanner.nextLine();
        
        // Remove spaces and convert to lowercase
        String cleanS1 = s1.replaceAll("\\s+", "").toLowerCase();
        String cleanS2 = s2.replaceAll("\\s+", "").toLowerCase();
        
        // Check if lengths are different
        if (cleanS1.length() != cleanS2.length()) {
            System.out.println("No");
            return;
        }
        
        // Convert to char arrays and sort
        char[] arr1 = cleanS1.toCharArray();
        char[] arr2 = cleanS2.toCharArray();
        
        Arrays.sort(arr1);
        Arrays.sort(arr2);
        
        // Compare sorted arrays
        boolean isAnagram = Arrays.equals(arr1, arr2);
        
        System.out.println(isAnagram ? "Yes" : "No");
    }
}
