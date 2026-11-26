import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String s = scanner.nextLine();
        scanner.close();

        s = s.trim();
        if (s.isEmpty()) {
            System.out.println(0);
        } else {
            String[] words = s.split(" +");
            System.out.println(words.length);
        }
    }
}
