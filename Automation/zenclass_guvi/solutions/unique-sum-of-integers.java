import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int n = scanner.nextInt();
        Set<Integer> uniqueNumbers = new HashSet<>();
        for (int i = 0; i < n; i++) {
            uniqueNumbers.add(scanner.nextInt());
        }
        int sum = 0;
        for (Integer num : uniqueNumbers) {
            sum += num; // using Integer wrapper class method intValue() implicitly
        }
        System.out.println(sum);
    }
}
