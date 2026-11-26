import java.util.*;

@FunctionalInterface
interface LongestStringFinder {
    int findLength(List<String> list);
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        sc.nextLine();
        List<String> list = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            list.add(sc.nextLine());
        }
        
        LongestStringFinder finder = (strings) -> {
            if (strings == null || strings.isEmpty()) return 0;
            int maxLen = 0;
            for (String s : strings) {
                if (s != null && s.length() > maxLen) {
                    maxLen = s.length();
                }
            }
            return maxLen;
        };
        
        System.out.println(finder.findLength(list));
    }
}
