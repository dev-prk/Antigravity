import java.util.*;

class Pair<T, U> {
    private T first;
    private U second;

    public Pair(T first, U second) {
        this.first = first;
        this.second = second;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Pair)) return false;
        Pair<?, ?> p = (Pair<?, ?>) o;
        return Objects.equals(first, p.first) && Objects.equals(second, p.second);
    }

    @Override
    public int hashCode() {
        return Objects.hash(first, second);
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        while (scanner.hasNext()) {
            if (!scanner.hasNextInt()) break;
            int i1 = scanner.nextInt();
            if (!scanner.hasNext()) break;
            String s1 = scanner.next();
            if (!scanner.hasNextInt()) break;
            int i2 = scanner.nextInt();
            if (!scanner.hasNext()) break;
            String s2 = scanner.next();

            Pair<Integer, String> p1 = new Pair<>(i1, s1);
            Pair<Integer, String> p2 = new Pair<>(i2, s2);

            if (p1.equals(p2)) {
                System.out.println("The pairs are equal.");
            } else {
                System.out.println("The pairs are not equal.");
            }
        }
        scanner.close();
    }
}
