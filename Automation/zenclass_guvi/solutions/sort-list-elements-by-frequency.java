import java.util.*;
import java.util.stream.Collectors;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        if (!sc.hasNextInt()) {
            System.out.println(-1);
            return;
        }
        
        int n = sc.nextInt();
        
        List<Integer> elements = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            elements.add(sc.nextInt());
        }
        
        Map<Integer, Integer> freq = new LinkedHashMap<>();
        for (int elem : elements) {
            freq.put(elem, freq.getOrDefault(elem, 0) + 1);
        }
        
        List<Map.Entry<Integer, Integer>> sorted = freq.entrySet()
            .stream()
            .sorted((a, b) -> {
                int cmp = Integer.compare(b.getValue(), a.getValue());
                if (cmp == 0) {
                    return 0;
                }
                return cmp;
            })
            .collect(Collectors.toList());
        
        for (Map.Entry<Integer, Integer> entry : sorted) {
            System.out.println(entry.getKey() + ":" + entry.getValue());
        }
    }
}
