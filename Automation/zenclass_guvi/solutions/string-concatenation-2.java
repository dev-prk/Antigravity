import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s1 = br.readLine();
        if (s1 == null) s1 = "";
        String s2 = br.readLine();
        if (s2 == null) s2 = "";
        System.out.print(s1 + s2);
    }
}
