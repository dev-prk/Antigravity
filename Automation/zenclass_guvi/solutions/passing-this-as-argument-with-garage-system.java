import java.util.*;

class Car {
    private String brand;
    private String model;

    public Car(String brand, String model) {
        this.brand = brand;
        this.model = model;
    }

    public String getBrand() {
        return brand;
    }

    public String getModel() {
        return model;
    }

    public void park(Garage garage) {
        garage.parkCar(this);
    }
}

class Garage {
    private List<Car> parkedCars;
    private int slotCounter;

    public Garage() {
        parkedCars = new ArrayList<>();
        slotCounter = 1;
    }

    public void parkCar(Car c) {
        System.out.println("Car " + c.getBrand() + " " + c.getModel() + " has been parked in slot #" + slotCounter);
        parkedCars.add(c);
        slotCounter++;
    }

    public void displayStatus() {
        System.out.println("\n--- Garage Status ---");
        for (int i = 0; i < parkedCars.size(); i++) {
            Car c = parkedCars.get(i);
            System.out.println("Slot " + (i + 1) + ": " + c.getBrand() + " " + c.getModel());
        }
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        sc.nextLine(); // consume newline
        
        Garage garage = new Garage();
        
        for (int i = 0; i < n; i++) {
            String brand = sc.nextLine();
            String model = sc.nextLine();
            Car car = new Car(brand, model);
            car.park(garage);
        }
        
        garage.displayStatus();
        
        sc.close();
    }
}
