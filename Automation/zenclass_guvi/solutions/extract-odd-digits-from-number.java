import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null || line.isEmpty()) {
            System.out.println(-1);
            return;
        }
        line = line.trim();
        if (line.isEmpty()) {
            System.out.println(-1);
            return;
        }
        List<Integer> odds = new ArrayList<>();
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (Character.isDigit(c)) {
                int d = c - '0';
                if (d % 2 == 1) {
                    odds.add(d);
                }
            }
        }
        if (odds.isEmpty()) {
            System.out.println(-1);
        } else {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < odds.size(); i++) {
                if (i > 0) sb.append(' ');
                sb.append(odds.get(i));
            }
            System.out.println(sb.toString());
        }
    }
}
