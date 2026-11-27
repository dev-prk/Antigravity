import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String text = br.readLine();
        String pattern = br.readLine();
        
        if (isMatch(text, pattern)) {
            System.out.println("YES");
        } else {
            System.out.println("NO");
        }
    }
    
    static boolean isMatch(String text, String pattern) {
        // Handle edge cases
        if (text == null || pattern == null) return false;
        if (pattern.isEmpty()) return text.isEmpty();
        
        // First, preprocess pattern to merge consecutive wildcards
        StringBuilder mergedPattern = new StringBuilder();
        boolean prevWasWildcard = false;
        for (int i = 0; i < pattern.length(); i++) {
            char c = pattern.charAt(i);
            if (c == '?' || c == '*') {
                if (!prevWasWildcard) {
                    mergedPattern.append(c);
                    prevWasWildcard = true;
                }
            } else {
                mergedPattern.append(c);
                prevWasWildcard = false;
            }
        }
        pattern = mergedPattern.toString();
        
        // Count wildcards in pattern
        int starCount = 0;
        int questionCount = 0;
        for (char c : pattern.toCharArray()) {
            if (c == '*') starCount++;
            else if (c == '?') questionCount++;
        }
        
        // If no wildcards, direct comparison
        if (starCount == 0 && questionCount == 0) {
            return text.equals(pattern);
        }
        
        // Build a regex pattern
        StringBuilder regex = new StringBuilder();
        regex.append("^");
        
        for (char c : pattern.toCharArray()) {
            if (c == '?') {
                regex.append(".");
            } else if (c == '*') {
                regex.append(".*");
            } else {
                regex.append(Character.toString(c));
            }
        }
        
        regex.append("$");
        
        String regexStr = regex.toString();
        // Use built-in regex matching for correctness
        return text.matches(regexStr);
    }
}
