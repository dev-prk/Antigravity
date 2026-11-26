import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();
        StringTokenizer st = new StringTokenizer(br.readLine());
        while (st.hasMoreTokens()) {
            int month = Integer.parseInt(st.nextToken());
            int year = Integer.parseInt(st.nextToken());
            if (month == -1 && year == -1) {
                break;
            }
            sb.append(daysInMonth(month, year)).append("\n");
            while (!st.hasMoreTokens() && !br.readLine().isEmpty()) {
                st = new StringTokenizer(br.readLine());
            }
            while (st.hasMoreTokens()) {
                month = Integer.parseInt(st.nextToken());
                year = Integer.parseInt(st.nextToken());
                if (month == -1 && year == -1) {
                    break;
                }
                sb.append(daysInMonth(month, year)).append("\n");
            }
            if (month == -1 && year == -1) {
                break;
            }
        }
        System.out.print(sb.toString());
    }
    
    static int daysInMonth(int month, int year) {
        switch (month) {
            case 1: case 3: case 5: case 7: case 8: case 10: case 12:
                return 31;
            case 4: case 6: case 9: case 11:
                return 30;
            case 2:
                if (isLeapYear(year)) {
                    return 29;
                } else {
                    return 28;
                }
            default:
                return -1;
        }
    }
    
    static boolean isLeapYear(int year) {
        if (year % 400 == 0) {
            return true;
        }
        if (year % 100 == 0) {
            return false;
        }
        if (year % 4 == 0) {
            return true;
        }
        return false;
    }
}
