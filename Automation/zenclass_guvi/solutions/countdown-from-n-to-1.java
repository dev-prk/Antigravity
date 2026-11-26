import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null || line.isEmpty()) {
            return;
        }
        int n = Integer.parseInt(line.trim());
        for (int i = n; i >= 1; i--) {
            System.out.println(i);
        }
    }
}
