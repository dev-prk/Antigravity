import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null) {
            s = "";
        }
        String[] parts = s.trim().split("\\s+");
        if (parts.length == 1 && parts[0].isEmpty()) {
            System.out.println();
            return;
        }
        StringBuilder sb = new StringBuilder();
        for (int i = parts.length - 1; i >= 0; i--) {
            sb.append(parts[i]);
            if (i > 0) {
                sb.append(' ');
            }
        }
        System.out.println(sb.toString());
    }
}
