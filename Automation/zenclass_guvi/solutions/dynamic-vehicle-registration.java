import java.util.Scanner;

class Vehicle {
    protected String registrationNumber;
    protected String ownerName;
    
    public Vehicle(String registrationNumber, String ownerName) {
        this.registrationNumber = registrationNumber;
        this.ownerName = ownerName;
    }
    
    public void displayDetails() {
        System.out.println("Vehicle: " + this.getClass().getSimpleName());
        System.out.println("Registration Number: " + registrationNumber);
        System.out.println("Owner: " + ownerName);
    }
}

class Car extends Vehicle {
    private int numberOfDoors;
    
    public Car(String registrationNumber, String ownerName, int numberOfDoors) {
        super(registrationNumber, ownerName);
        this.numberOfDoors = numberOfDoors;
    }
    
    @Override
    public void displayDetails() {
        super.displayDetails();
        System.out.println("Number of Doors: " + numberOfDoors);
    }
}

class Motorcycle extends Vehicle {
    private String engineCapacity;
    
    public Motorcycle(String registrationNumber, String ownerName, String engineCapacity) {
        super(registrationNumber, ownerName);
        this.engineCapacity = engineCapacity;
    }
    
    @Override
    public void displayDetails() {
        super.displayDetails();
        System.out.println("Engine Capacity: " + engineCapacity);
    }
}

class Truck extends Vehicle {
    private String cargoCapacity;
    
    public Truck(String registrationNumber, String ownerName, String cargoCapacity) {
        super(registrationNumber, ownerName);
        this.cargoCapacity = cargoCapacity;
    }
    
    @Override
    public void displayDetails() {
        super.displayDetails();
        System.out.println("Cargo Capacity: " + cargoCapacity);
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        sc.nextLine();
        
        for (int i = 0; i < N; i++) {
            String line = sc.nextLine();
            String[] parts = line.split(" ", 4);
            
            String type = parts[1];
            String regNum = parts[2];
            String owner = parts[3].split(" ")[0];
            String specificAttr = parts[3].substring(parts[3].indexOf(owner) + owner.length() + 1);
            
            Vehicle v = null;
            if (type.equals("Car")) {
                int doors = Integer.parseInt(specificAttr);
                v = new Car(regNum, owner, doors);
            } else if (type.equals("Motorcycle")) {
                v = new Motorcycle(regNum, owner, specificAttr);
            } else if (type.equals("Truck")) {
                v = new Truck(regNum, owner, specificAttr);
            }
            
            v.displayDetails();
        }
        
        sc.close();
    }
}
