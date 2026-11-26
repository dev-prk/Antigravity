import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        sc.close();
        
        List<List<String>> solutions = solveNQueens(N);
        
        if (solutions.isEmpty()) {
            System.out.println("No solution");
        } else {
            for (int i = 0; i < solutions.size(); i++) {
                List<String> solution = solutions.get(i);
                for (int j = 0; j < solution.size(); j++) {
                    System.out.println(solution.get(j));
                }
                if (i < solutions.size() - 1) {
                    System.out.println();
                }
            }
        }
    }
    
    public static List<List<String>> solveNQueens(int n) {
        List<List<String>> solutions = new ArrayList<>();
        if (n <= 0) {
            return solutions;
        }
        
        int[] queens = new int[n]; // queens[i] = column position of queen in row i
        backtrack(solutions, queens, 0, n);
        return solutions;
    }
    
    private static void backtrack(List<List<String>> solutions, int[] queens, int row, int n) {
        if (row == n) {
            solutions.add(buildBoard(queens, n));
            return;
        }
        
        for (int col = 0; col < n; col++) {
            if (isSafe(queens, row, col)) {
                queens[row] = col;
                backtrack(solutions, queens, row + 1, n);
            }
        }
    }
    
    private static boolean isSafe(int[] queens, int row, int col) {
        for (int i = 0; i < row; i++) {
            // Check column
            if (queens[i] == col) {
                return false;
            }
            // Check diagonal
            if (Math.abs(queens[i] - col) == row - i) {
                return false;
            }
        }
        return true;
    }
    
    private static List<String> buildBoard(int[] queens, int n) {
        List<String> board = new ArrayList<>();
        for (int row = 0; row < n; row++) {
            StringBuilder sb = new StringBuilder();
            for (int col = 0; col < n; col++) {
                if (queens[row] == col) {
                    sb.append('Q');
                } else {
                    sb.append('.');
                }
            }
            board.add(sb.toString());
        }
        return board;
    }
}
