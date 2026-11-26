import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s != null) {
            s = s.trim();
        }
        System.out.println(isValidJavaIdentifier(s));
    }

    private static final Set<String> KEYWORDS = new HashSet<>(Arrays.asList(
        "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char",
        "class", "const", "continue", "default", "do", "double", "else", "enum",
        "extends", "final", "finally", "float", "for", "goto", "if", "implements",
        "import", "instanceof", "int", "interface", "long", "native", "new", "package",
        "private", "protected", "public", "return", "short", "static", "strictfp",
        "super", "switch", "synchronized", "this", "throw", "throws", "transient",
        "try", "void", "volatile", "while"
    ));

    public static boolean isValidJavaIdentifier(String str) {
        if (str == null || str.isEmpty()) {
            return false;
        }

        // Check if it's a Java keyword
        if (KEYWORDS.contains(str)) {
            return false;
        }

        // Check first character: must be letter or underscore
        char first = str.charAt(0);
        if (!isLetter(first) && first != '_') {
            return false;
        }

        // Check remaining characters: can be letter, digit, or underscore
        for (int i = 1; i < str.length(); i++) {
            char c = str.charAt(i);
            if (!isLetter(c) && !Character.isDigit(c) && c != '_') {
                return false;
            }
        }

        return true;
    }

    private static boolean isLetter(char c) {
        return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
    }
}
