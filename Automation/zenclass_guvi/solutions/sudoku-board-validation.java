import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        char[][] board = new char[9][9];
        
        for (int i = 0; i < 9; i++) {
            String line = br.readLine();
            if (line == null) break;
            StringTokenizer st = new StringTokenizer(line);
            for (int j = 0; j < 9; j++) {
                if (st.hasMoreTokens()) {
                    board[i][j] = st.nextToken().charAt(0);
                } else {
                    board[i][j] = '.';
                }
            }
        }
        
        System.out.println(isValidSudoku(board));
    }
    
    public static boolean isValidSudoku(char[][] board) {
        // Validate rows
        for (int i = 0; i < 9; i++) {
            if (!isValidGroup(board, i, 0, 9, 1)) {
                return false;
            }
        }
        
        // Validate columns
        for (int j = 0; j < 9; j++) {
            if (!isValidGroup(board, 0, j, 9, 0)) {
                return false;
            }
        }
        
        // Validate 3x3 sub-boxes
        for (int box = 0; box < 9; box++) {
            int startRow = (box / 3) * 3;
            int startCol = (box % 3) * 3;
            if (!isValidGroup(board, startRow, startCol, 3, 1)) {
                return false;
            }
            if (!isValidSubBox(board, startRow, startCol)) {
                return false;
            }
        }
        
        return true;
    }
    
    public static boolean isValidGroup(char[][] board, int startRow, int startCol, int size, int mode) {
        Set<Character> seen = new HashSet<>();
        for (int i = 0; i < size; i++) {
            char c;
            if (mode == 1) { // Row
                c = board[startRow][startCol + i];
            } else { // Column
                c = board[startRow + i][startCol];
            }
            if (c != '.') {
                if (seen.contains(c)) {
                    return false;
                }
                seen.add(c);
            }
        }
        return true;
    }
    
    public static boolean isValidSubBox(char[][] board, int startRow, int startCol) {
        Set<Character> seen = new HashSet<>();
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                char c = board[startRow + i][startCol + j];
                if (c != '.') {
                    if (seen.contains(c)) {
                        return false;
                    }
                    seen.add(c);
                }
            }
        }
        return true;
    }
}
