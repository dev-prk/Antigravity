import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int rows = Integer.parseInt(parts[0]);
        int cols = Integer.parseInt(parts[1]);
        
        int[][] matrix = new int[rows][cols];
        for (int i = 0; i < rows; i++) {
            parts = br.readLine().trim().split("\\s+");
            for (int j = 0; j < cols; j++) {
                matrix[i][j] = Integer.parseInt(parts[j]);
            }
        }
        
        int target = Integer.parseInt(br.readLine().trim());
        
        int result = searchMatrix(matrix, target);
        if (result == -1) {
            System.out.println(-1);
        } else {
            int row = result / cols;
            int col = result % cols;
            System.out.println(row + " " + col);
        }
    }
    
    private static int searchMatrix(int[][] matrix, int target) {
        int rows = matrix.length;
        if (rows == 0) return -1;
        int cols = matrix[0].length;
        if (cols == 0) return -1;
        
        int left = 0, right = rows * cols - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            int midRow = mid / cols;
            int midCol = mid % cols;
            int midVal = matrix[midRow][midCol];
            
            if (midVal == target) {
                return mid;
            } else if (midVal < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return -1;
    }
}
