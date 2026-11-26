import java.io.*;
public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null) {
            System.out.println(0);
            return;
        }
        int count = 0;
        for (int i = 0; i < s.length(); i++) {
            count++;
        }
        System.out.println(count);
    }
}
