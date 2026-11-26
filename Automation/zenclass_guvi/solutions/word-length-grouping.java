import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        sc.nextLine();
        String line = sc.nextLine();
        String[] words = line.split(" ");
        Map<Integer, List<String>> map = new TreeMap<>();
        for (String word : words) {
            int len = word.length();
            map.putIfAbsent(len, new ArrayList<>());
            map.get(len).add(word);
        }
        for (Map.Entry<Integer, List<String>> entry : map.entrySet()) {
            System.out.print(entry.getKey() + ": " + entry.getValue().toString().replace("[", "[").replace("]", "]"));
            System.out.println();
        }
        sc.close();
    }
}
