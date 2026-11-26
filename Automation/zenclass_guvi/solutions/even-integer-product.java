import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null) {
            System.out.println(0);
            return;
        }
        line = line.trim();
        if (line.isEmpty()) {
            System.out.println(0);
            return;
        }
        int n;
        try {
            n = Integer.parseInt(line);
        } catch (NumberFormatException e) {
            System.out.println(0);
            return;
        }

        long product = 1L;
        boolean hasEven = false;
        int readCount = 0;

        while (readCount < n) {
            String dataLine = br.readLine();
            if (dataLine == null) break;
            StringTokenizer st = new StringTokenizer(dataLine);
            while (st.hasMoreTokens() && readCount < n) {
                String token = st.nextToken();
                int value;
                try {
                    value = Integer.parseInt(token);
                } catch (NumberFormatException e) {
                    continue; // skip invalid token
                }
                if (value % 2 == 0) {
                    product *= value;
                    hasEven = true;
                }
                readCount++;
            }
        }

        if (!hasEven) {
            System.out.println(0);
        } else {
            System.out.println(product);
        }
    }
}
