import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        int count1 = 0; // 0 to 10
        int count2 = 0; // 11 to 20
        int count3 = 0; // 21 to 30
        int count4 = 0; // 31 and above
        
        while (true) {
            int num = scanner.nextInt();
            if (num < 0) {
                break;
            }
            
            if (num >= 0 && num <= 10) {
                count1++;
            } else if (num >= 11 && num <= 20) {
                count2++;
            } else if (num >= 21 && num <= 30) {
                count3++;
            } else if (num >= 31) {
                count4++;
            }
        }
        
        System.out.println(count1 + " " + count2 + " " + count3 + " " + count4);
    }
}
