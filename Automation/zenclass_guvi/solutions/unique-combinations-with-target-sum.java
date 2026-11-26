import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] line1 = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(line1[0]);
        int target = Integer.parseInt(line1[1]);
        
        String[] line2 = br.readLine().trim().split("\\s+");
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(line2[i]);
        }
        Arrays.sort(arr);
        
        List<List<Integer>> result = new ArrayList<>();
        backtrack(arr, target, 0, new ArrayList<>(), result);
        
        if (result.isEmpty()) {
            System.out.println("No combination found");
        } else {
            for (List<Integer> combo : result) {
                for (int i = 0; i < combo.size(); i++) {
                    if (i > 0) System.out.print(" ");
                    System.out.print(combo.get(i));
                }
                System.out.println();
            }
        }
    }
    
    private static void backtrack(int[] arr, int target, int start, List<Integer> current, List<List<Integer>> result) {
        if (target == 0) {
            result.add(new ArrayList<>(current));
            return;
        }
        if (target < 0) {
            return;
        }
        
        for (int i = start; i < arr.length; i++) {
            if (arr[i] > target) break;
            current.add(arr[i]);
            backtrack(arr, target - arr[i], i, current, result);
            current.remove(current.size() - 1);
        }
    }
}
