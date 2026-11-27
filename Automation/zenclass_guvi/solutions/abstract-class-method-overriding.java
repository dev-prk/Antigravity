import java.util.*;
import java.text.DecimalFormat;

abstract class Vehicle {
    abstract double fuelEfficiency();
}

class Car extends Vehicle {
    private double distance;
    private double fuel;

    public Car(double distance, double fuel) {
        this.distance = distance;
        this.fuel = fuel;
    }

    @Override
    double fuelEfficiency() {
        return distance / fuel;
    }
}

class Truck extends Vehicle {
    private double distance;
    private double fuel;

    public Truck(double distance, double fuel) {
        this.distance = distance;
        this.fuel = fuel;
    }

    @Override
    double fuelEfficiency() {
        return (distance * 0.8) / fuel;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        if (!sc.hasNextLine()) {
            System.out.println(-1);
            return;
        }
        
        String line = sc.nextLine().trim();
        sc.close();
        
        if (line.isEmpty()) {
            System.out.println(-1);
            return;
        }
        
        String[] parts = line.split("\\s+");
        if (parts.length < 3) {
            System.out.println(-1);
            return;
        }
        
        try {
            String vehicleType = parts[0];
            double distance = Double.parseDouble(parts[1]);
            double fuel = Double.parseDouble(parts[2]);
            
            Vehicle v;
            if (vehicleType.equalsIgnoreCase("Car")) {
                v = new Car(distance, fuel);
            } else if (vehicleType.equalsIgnoreCase("Truck")) {
                v = new Truck(distance, fuel);
            } else {
                System.out.println(-1);
                return;
            }
            
            double efficiency = v.fuelEfficiency();
            DecimalFormat df = new DecimalFormat("#.0");
            System.out.println("Fuel Efficiency: " + df.format(efficiency));
        } catch (NumberFormatException e) {
            System.out.println(-1);
        }
    }
}
