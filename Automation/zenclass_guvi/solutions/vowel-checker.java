import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        Scanner sc = new Scanner(System.in);
        String input = sc.nextLine();
        if (input.isEmpty()) {
            System.out.println("Not Vowel");
            return;
        }
        char c = input.trim().charAt(0);
        if (!Character.isLetter(c)) {
            System.out.println("Not Vowel");
            return;
        }
        c = Character.toLowerCase(c);
        if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') {
            System.out.println("Vowel");
        } else {
            System.out.println("Not Vowel");
        }
    }
}
