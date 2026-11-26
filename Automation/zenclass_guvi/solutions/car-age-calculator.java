import java.util.Scanner;

class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String make = scanner.next();
        String model = scanner.next();
        int year = scanner.nextInt();
        int currentYear = scanner.nextInt();

        Car car = new Car(make, model, year);
        int age = car.getCarAge(currentYear);

        if (age != -1) {
            System.out.println(age);
        }
    }
}

class Car {
    private String make;
    private String model;
    private int year;

    public Car(String make, String model, int year) {
        this.make = make;
        this.model = model;
        this.year = year;
    }

    public int getCarAge(int currentYear) {
        if (year > currentYear) {
            System.out.println("Invalid year");
            return -1;
        }
        return currentYear - year;
    }
}
