import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String s = sc.nextLine();
            int count = 0;
            String vowels = "aeiouAEIOU";
            for (int i = 0; i < s.length(); i++) {
                if (vowels.indexOf(s.charAt(i)) != -1) {
                    count++;
                }
            }
            System.out.println(count);
        }
    }
}
