import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.println(max(a, b));
        sc.close();
    }
    
    public static int max(int x, int y) {
        return (x > y) ? x : y;
    }
}
