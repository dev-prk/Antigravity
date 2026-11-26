import java.util.Scanner;

interface Employee {
    double calculateSalary();
    String getDetails();
}

class FullTimeEmployee implements Employee {
    private String name;
    private double monthlySalary;

    public FullTimeEmployee(String name, double monthlySalary) {
        this.name = name;
        this.monthlySalary = monthlySalary;
    }

    @Override
    public double calculateSalary() {
        return monthlySalary;
    }

    @Override
    public String getDetails() {
        return "Name: " + name + ", Salary: " + calculateSalary();
    }
}

class PartTimeEmployee implements Employee {
    private String name;
    private double hourlyRate;
    private int hoursWorked;

    public PartTimeEmployee(String name, double hourlyRate, int hoursWorked) {
        this.name = name;
        this.hourlyRate = hourlyRate;
        this.hoursWorked = hoursWorked;
    }

    @Override
    public double calculateSalary() {
        return hourlyRate * hoursWorked;
    }

    @Override
    public String getDetails() {
        return "Name: " + name + ", Salary: " + calculateSalary();
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String employeeType = scanner.next();
        Employee employee;

        if (employeeType.equals("FullTimeEmployee")) {
            String name = scanner.next();
            double monthlySalary = scanner.nextDouble();
            employee = new FullTimeEmployee(name, monthlySalary);
        } else {
            String name = scanner.next();
            double hourlyRate = scanner.nextDouble();
            int hoursWorked = scanner.nextInt();
            employee = new PartTimeEmployee(name, hourlyRate, hoursWorked);
        }

        System.out.println(employee.getDetails());
    }
}
