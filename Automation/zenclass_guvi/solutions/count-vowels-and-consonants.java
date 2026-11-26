import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();
        sc.close();

        int vowels = 0;
        int consonants = 0;

        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (Character.isLetter(ch)) {
                char lower = Character.toLowerCase(ch);
                if (lower == 'a' || lower == 'e' || lower == 'i' || lower == 'o' || lower == 'u') {
                    vowels++;
                } else {
                    consonants++;
                }
            }
        }

        System.out.println(vowels + " " + consonants);
    }
}
