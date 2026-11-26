import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        
        if (line == null || line.trim().isEmpty()) {
            System.out.println("-1 -1");
            return;
        }
        
        String[] parts = line.trim().split("\\s+");
        
        if (parts.length == 0 || (parts.length == 1 && parts[0].isEmpty())) {
            System.out.println("-1 -1");
            return;
        }
        
        int front = -1;
        int rear = -1;
        
        for (int i = 0; i < parts.length; i++) {
            if (!parts[i].isEmpty()) {
                int num = Integer.parseInt(parts[i]);
                if (i == 0) {
                    front = num;
                }
                rear = num;
            }
        }
        
        if (front == -1 && rear == -1) {
            System.out.println("-1 -1");
        } else {
            System.out.println(front + " " + rear);
        }
    }
}
