import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int N = scanner.nextInt();
        towerOfHanoi(N, 'A', 'C', 'B');
    }

    public static void towerOfHanoi(int n, char source, char destination, char auxiliary) {
        if (n == 1) {
            System.out.println("Move disk 1 from rod " + source + " to rod " + destination);
            return;
        }
        towerOfHanoi(n - 1, source, auxiliary, destination);
        System.out.println("Move disk " + n + " from rod " + source + " to rod " + destination);
        towerOfHanoi(n - 1, auxiliary, destination, source);
    }
}
