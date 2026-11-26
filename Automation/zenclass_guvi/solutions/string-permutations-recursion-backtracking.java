import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null) return;
        line = line.trim();
        if (line.isEmpty()) {
            return;
        }

        char[] chars = line.toCharArray();
        Arrays.sort(chars);

        List<String> result = new ArrayList<>();
        boolean[] used = new boolean[chars.length];
        backtrack(chars, used, new StringBuilder(), result);

        StringBuilder out = new StringBuilder();
        for (String s : result) {
            out.append(s).append('\n');
        }
        System.out.print(out.toString());
    }

    private static void backtrack(char[] chars, boolean[] used, StringBuilder sb, List<String> result) {
        if (sb.length() == chars.length) {
            result.add(sb.toString());
            return;
        }

        for (int i = 0; i < chars.length; i++) {
            if (used[i]) continue;

            // Skip duplicates: if the same character was used at the same position in a previous iteration, skip
            if (i > 0 && chars[i] == chars[i - 1] && !used[i - 1]) {
                continue;
            }

            used[i] = true;
            sb.append(chars[i]);
            backtrack(chars, used, sb, result);
            sb.setLength(sb.length() - 1);
            used[i] = false;
        }
    }
}
