import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String line = sc.nextLine();
        if (line == null || line.isEmpty()) {
            System.out.println(0);
            return;
        }
        String[] words = line.trim().split("\\s+");
        Set<String> unique = new HashSet<>();
        for (String w : words) {
            unique.add(w.toLowerCase());
        }
        System.out.println(unique.size());
    }
}
