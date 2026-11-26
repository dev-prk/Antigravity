import java.util.LinkedHashSet;
import java.util.Scanner;
import java.util.Set;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = Integer.parseInt(sc.nextLine());
        Set<String> set = new LinkedHashSet<>();
        
        for (int i = 0; i < N; i++) {
            String line = sc.nextLine();
            String op = line.substring(0, line.indexOf(' '));
            String item = line.substring(line.indexOf(' ') + 1);
            
            if (op.equals("ADD")) {
                set.add(item);
            } else if (op.equals("REMOVE")) {
                set.remove(item);
            }
        }
        
        boolean first = true;
        for (String item : set) {
            if (!first) {
                System.out.print(", ");
            }
            System.out.print(item);
            first = false;
        }
        System.out.println();
    }
}
