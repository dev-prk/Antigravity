public class Main {
    public static void main(String[] args) {
        java.util.Scanner sc = new java.util.Scanner(System.in);
        if (sc.hasNext()) {
            sc.next(); // name
            int id = sc.nextInt();
            int basicSalary = sc.nextInt();
            int bonus = sc.nextInt();
            int total = basicSalary + bonus;
            System.out.println(total);
        }
    }
}
