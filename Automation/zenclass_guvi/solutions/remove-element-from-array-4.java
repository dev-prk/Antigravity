import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        int remove = sc.nextInt();
        
        List<Integer> resultList = new ArrayList<>();
        for (int num : arr) {
            if (num != remove) {
                resultList.add(num);
            }
        }
        
        for (int i = 0; i < resultList.size(); i++) {
            if (i > 0) {
                System.out.print(" ");
            }
            System.out.print(resultList.get(i));
        }
        System.out.println();
        
        sc.close();
    }
}
