import java.util.*;
import java.util.stream.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        sc.nextLine();
        String line = sc.nextLine();
        List<String> list = Arrays.asList(line.split("\\s+"));
        list = list.stream().filter(s -> !s.isEmpty()).collect(Collectors.toList());
        sortList(list);
        System.out.println(String.join(" ", list));
        sc.close();
    }
    
    public static <T extends Comparable<T>> void sortList(List<T> list) {
        Collections.sort(list);
    }
}
