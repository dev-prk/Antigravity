import java.util.*;
import java.util.stream.*;

public class Main {
    static class DigitSum {
        private int digitSum;

        public DigitSum(int num) {
            this.digitSum = computeDigitSum(Math.abs(num));
        }

        private int computeDigitSum(int n) {
            int sum = 0;
            while (n > 0) {
                sum += n % 10;
                n /= 10;
            }
            return sum;
        }

        public int getDigitSum() {
            return digitSum;
        }

        public static int getTotalDigitSum(DigitSum... objects) {
            return Arrays.stream(objects)
                    .mapToInt(DigitSum::getDigitSum)
                    .sum();
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        List<Integer> numbers = new ArrayList<>();
        while (sc.hasNextInt()) {
            numbers.add(sc.nextInt());
        }
        sc.close();

        if (numbers.isEmpty()) {
            System.out.println(0);
            return;
        }

        DigitSum[] objects = numbers.stream()
                .map(DigitSum::new)
                .toArray(DigitSum[]::new);

        System.out.println(DigitSum.getTotalDigitSum(objects));
    }
}
