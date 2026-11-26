import java.util.Scanner;

public class Main {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        String inputStr = scanner.nextLine();

        String lowercaseStr = inputStr.toLowerCase();

        System.out.println(lowercaseStr);
    }
}
