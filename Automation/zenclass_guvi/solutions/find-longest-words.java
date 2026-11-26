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
            sc.close();
            return;
        }
        
        List<String> words = new ArrayList<>();
        int maxLen = 0;
        
        for (int i = 0; i < n; i++) {
            if (sc.hasNextLine()) {
                String line = sc.nextLine();
                String trimmed = line.trim();
                if (!trimmed.isEmpty()) {
                    words.add(trimmed);
                    if (trimmed.length() > maxLen) {
                        maxLen = trimmed.length();
                    }
                }
            }
        }
        
        for (String word : words) {
            if (word.length() == maxLen) {
                System.out.println(word);
            }
        }
        
        sc.close();
    }
}
