import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        sc.nextLine(); // consume end-of-line after n
        String line1 = sc.nextLine();
        String line2 = sc.nextLine();
        String[] parts1 = line1.trim().split("\\s+");
        String[] parts2 = line2.trim().split("\\s+");
        int[] arr1 = new int[n];
        int[] arr2 = new int[n];
        for (int i = 0; i < n; i++) {
            arr1[i] = Integer.parseInt(parts1[i]);
            arr2[i] = Integer.parseInt(parts2[i]);
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(arr1[i] + arr2[i]);
        }
        System.out.println(sb.toString());
    }
}
