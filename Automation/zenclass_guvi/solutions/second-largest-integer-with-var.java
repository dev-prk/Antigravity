import java.util.*;

public class Main {
    public static void main(String[] args) {
        //..... YOUR CODE STARTS HERE .....
        var scanner = new Scanner(System.in);
        var n = scanner.nextInt();
        var numbers = new ArrayList<Integer>();
        for (var i = 0; i < n; i++) {
            numbers.add(scanner.nextInt());
        }
        Collections.sort(numbers);
        System.out.println(numbers.get(n - 2));
        //..... YOUR CODE ENDS HERE .....
    }
}
