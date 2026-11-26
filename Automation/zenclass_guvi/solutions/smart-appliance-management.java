import java.util.ArrayList;
import java.util.Scanner;

class Appliance {
    private int id;
    private String name;
    private double powerRating;
    private boolean status;
    
    public Appliance(int id, String name, double powerRating, boolean status) {
        this.id = id;
        this.name = name;
        this.powerRating = powerRating;
        this.status = status;
    }
    
    public int getId() {
        return id;
    }
    
    public String getName() {
        return name;
    }
    
    public double getPowerRating() {
        return powerRating;
    }
    
    public boolean getStatus() {
        return status;
    }
    
    public void setStatus(boolean status) {
        this.status = status;
    }
}

class SmartHome {
    private ArrayList<Appliance> appliances;
    
    public SmartHome() {
        appliances = new ArrayList<>();
    }
    
    public void addAppliance(Appliance appliance) {
        appliances.add(appliance);
    }
    
    public boolean removeAppliance(int id) {
        for (int i = 0; i < appliances.size(); i++) {
            if (appliances.get(i).getId() == id) {
                appliances.remove(i);
                return true;
            }
        }
        return false;
    }
    
    public boolean toggleAppliance(int id) {
        for (Appliance appliance : appliances) {
            if (appliance.getId() == id) {
                appliance.setStatus(!appliance.getStatus());
                return true;
            }
        }
        return false;
    }
    
    public double calculateTotalPower() {
        double total = 0.0;
        for (Appliance appliance : appliances) {
            if (appliance.getStatus()) {
                total += appliance.getPowerRating();
            }
        }
        return total;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        sc.nextLine();
        
        SmartHome smartHome = new SmartHome();
        
        for (int i = 0; i < n; i++) {
            int id = sc.nextInt();
            String name = sc.next();
            double powerRating = sc.nextDouble();
            String statusStr = sc.next();
            boolean status = statusStr.equals("on");
            Appliance appliance = new Appliance(id, name, powerRating, status);
            smartHome.addAppliance(appliance);
        }
        
        int m = sc.nextInt();
        sc.nextLine();
        
        for (int i = 0; i < m; i++) {
            String operation = sc.next();
            
            if (operation.equals("add")) {
                int id = sc.nextInt();
                String name = sc.next();
                double powerRating = sc.nextDouble();
                String statusStr = sc.next();
                boolean status = statusStr.equals("on");
                Appliance appliance = new Appliance(id, name, powerRating, status);
                smartHome.addAppliance(appliance);
            } else if (operation.equals("remove")) {
                int id = sc.nextInt();
                if (smartHome.removeAppliance(id)) {
                    System.out.println("Appliance removed successfully");
                } else {
                    System.out.println("Appliance not found");
                }
            } else if (operation.equals("toggle")) {
                int id = sc.nextInt();
                if (smartHome.toggleAppliance(id)) {
                    System.out.println("Appliance status toggled");
                } else {
                    System.out.println("Appliance not found");
                }
            } else if (operation.equals("calculate")) {
                double totalPower = smartHome.calculateTotalPower();
                System.out.printf("Total Power Consumption: %.1f kW\n", totalPower);
            }
        }
        
        sc.close();
    }
}
