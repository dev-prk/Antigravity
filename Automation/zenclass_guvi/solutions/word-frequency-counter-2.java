import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String line = sc.nextLine();
        String[] words = line.trim().split("\\s+");
        
        Map<String, Integer> freq = new HashMap<>();
        for (String word : words) {
            freq.put(word, freq.getOrDefault(word, 0) + 1);
        }
        
        List<Map.Entry<String, Integer>> list = new ArrayList<>(freq.entrySet());
        list.sort((a, b) -> {
            if (!a.getValue().equals(b.getValue())) {
                return b.getValue() - a.getValue();
            }
            return a.getKey().compareTo(b.getKey());
        });
        
        for (Map.Entry<String, Integer> e : list) {
            System.out.println(e.getKey() + " " + e.getValue());
        }
    }
}
