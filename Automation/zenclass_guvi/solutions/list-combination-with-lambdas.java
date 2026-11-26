import java.util.*;
import java.util.function.BiFunction;

@FunctionalInterface
interface Combiner {
    int combine(int a, int b);
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        sc.nextLine();
        
        List<Integer> list1 = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            list1.add(sc.nextInt());
        }
        
        List<Integer> list2 = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            list2.add(sc.nextInt());
        }
        
        Combiner adder = (a, b) -> a + b;
        
        List<Integer> result = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            result.add(adder.combine(list1.get(i), list2.get(i)));
        }
        
        for (int num : result) {
            System.out.println(num);
        }
    }
}
