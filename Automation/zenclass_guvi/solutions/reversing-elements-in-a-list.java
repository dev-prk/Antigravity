import java.util.*;
import java.util.stream.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        List<Integer> list = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            list.add(sc.nextInt());
        }
        
        ListIterator<Integer> it = list.listIterator(n);
        StringBuilder sb = new StringBuilder();
        while (it.hasPrevious()) {
            sb.append(it.previous());
            if (it.hasPrevious()) {
                sb.append(" ");
            }
        }
        sb.append(" ");
        
        System.out.println(sb.toString());
    }
}
