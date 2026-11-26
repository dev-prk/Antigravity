import java.util.*;
import java.util.stream.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        sc.nextLine(); // consume newline
        
        List<Integer> list = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            list.add(sc.nextInt());
        }
        
        List<Integer> unique = list.stream()
            .distinct()
            .collect(Collectors.toList());
        
        for (int num : unique) {
            System.out.println(num);
        }
    }
}
