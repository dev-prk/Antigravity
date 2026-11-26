import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int count = 0;
        int num = 1;
        
        while (count < n && num <= 50) {
            if (num % 3 == 0) {
                num++;
                continue;
            }
            if (count > 0) {
                System.out.print(" ");
            }
            System.out.print(num);
            count++;
            num++;
        }
        System.out.println();
    }
}
