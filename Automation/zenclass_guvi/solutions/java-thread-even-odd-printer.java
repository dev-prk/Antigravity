import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null || line.trim().isEmpty()) {
            return;
        }
        int n = Integer.parseInt(line.trim());
        
        Thread evenThread = new Thread(() -> {
            for (int i = 0; i <= n; i += 2) {
                System.out.println("Even Thread: " + i);
            }
        });
        
        Thread oddThread = new Thread(() -> {
            for (int i = 1; i <= n; i += 2) {
                System.out.println("Odd Thread: " + i);
            }
        });
        
        evenThread.start();
        oddThread.start();
        
        evenThread.join();
        oddThread.join();
    }
}
