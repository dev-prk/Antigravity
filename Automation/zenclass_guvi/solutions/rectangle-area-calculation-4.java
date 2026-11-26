import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line1 = br.readLine();
        String line2 = br.readLine();
        
        StringTokenizer st1 = new StringTokenizer(line1);
        StringTokenizer st2 = new StringTokenizer(line2);
        
        double a = Double.parseDouble(st1.nextToken().trim());
        double b = Double.parseDouble(st2.nextToken().trim());
        
        double area = a * b;
        
        // Check if area is an integer value
        if (area == Math.floor(area)) {
            System.out.println((long) area);
        } else {
            System.out.printf("%.1f%n", area);
        }
    }
}
