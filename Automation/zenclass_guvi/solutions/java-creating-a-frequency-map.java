import java.util.*;
import java.util.Map.Entry;
import java.util.stream.Collectors;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        sc.nextLine();
        
        String line = sc.nextLine();
        String[] words = line.split(" ");
        
        Map<String, Integer> freqMap = new LinkedHashMap<>();
        
        for (String word : words) {
            freqMap.put(word, freqMap.getOrDefault(word, 0) + 1);
        }
        
        Map<String, Integer> sortedDesc = freqMap.entrySet()
                .stream()
                .sorted(Entry.<String, Integer>comparingByValue().reversed())
                .collect(Collectors.toMap(
                        Entry::getKey,
                        Entry::getValue,
                        (e1, e2) -> e1,
                        LinkedHashMap::new
                ));
        
        for (Map.Entry<String, Integer> entry : sortedDesc.entrySet()) {
            System.out.println(entry.getKey() + " " + entry.getValue());
        }
        
        sc.close();
    }
}
