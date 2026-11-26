import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String input = scanner.nextLine();
        StringBuffer sb = new StringBuffer(input);
        System.out.println(sb.reverse().toString());
        scanner.close();
    }
}
