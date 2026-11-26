import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.util.StringTokenizer;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        
        int r = Integer.parseInt(st.nextToken());
        int c = Integer.parseInt(st.nextToken());
        
        int[][] matrix1 = new int[r][c];
        int[][] matrix2 = new int[r][c];
        
        // Read first matrix
        for (int i = 0; i < r; i++) {
            st = new StringTokenizer(br.readLine());
            for (int j = 0; j < c; j++) {
                matrix1[i][j] = Integer.parseInt(st.nextToken());
            }
        }
        
        // Read second matrix
        for (int i = 0; i < r; i++) {
            st = new StringTokenizer(br.readLine());
            for (int j = 0; j < c; j++) {
                matrix2[i][j] = Integer.parseInt(st.nextToken());
            }
        }
        
        // Subtract and print result
        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) {
                System.out.print(matrix1[i][j] - matrix2[i][j]);
                if (j < c - 1) {
                    System.out.print(" ");
                }
            }
            System.out.println();
        }
    }
}
