import java.util.*;
import java.util.stream.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        sc.nextLine();
        
        String line = sc.nextLine().trim();
        sc.close();
        
        if (n == 0 || line.isEmpty()) {
            return;
        }
        
        String[] parts = line.split("\\s+");
        
        List<String> stringList = Arrays.asList(parts);
        List<Integer> intList = new ArrayList<>();
        boolean isNumeric = true;
        
        for (String part : parts) {
            try {
                Integer.parseInt(part);
            } catch (NumberFormatException e) {
                isNumeric = false;
                break;
            }
        }
        
        if (isNumeric) {
            for (String part : parts) {
                intList.add(Integer.parseInt(part));
            }
            countFrequency(intList);
        } else {
            countFrequency(stringList);
        }
    }
    
    public static <T> void countFrequency(List<T> list) {
        HashMap<T, Integer> frequencyMap = new HashMap<>();
        
        for (T element : list) {
            frequencyMap.put(element, frequencyMap.getOrDefault(element, 0) + 1);
        }
        
        for (Map.Entry<T, Integer> entry : frequencyMap.entrySet()) {
            System.out.println(entry.getKey() + " -> " + entry.getValue());
        }
    }
}
