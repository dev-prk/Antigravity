import java.util.Scanner;

abstract class Insurance {
    protected double basePremium;
    
    public Insurance(double basePremium) {
        this.basePremium = basePremium;
    }
    
    public abstract double calculatePremium();
}

class LifeInsurance extends Insurance {
    public LifeInsurance(double basePremium) {
        super(basePremium);
    }
    
    @Override
    public double calculatePremium() {
        return basePremium * 1.10;
    }
}

class HealthInsurance extends Insurance {
    public HealthInsurance(double basePremium) {
        super(basePremium);
    }
    
    @Override
    public double calculatePremium() {
        return basePremium * 1.20;
    }
}

class CarInsurance extends Insurance {
    public CarInsurance(double basePremium) {
        super(basePremium);
    }
    
    @Override
    public double calculatePremium() {
        return basePremium * 1.30;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        String type = sc.nextLine().trim().toLowerCase();
        double base = sc.nextDouble();
        
        Insurance insurance = null;
        String insuranceType = "";
        
        switch (type) {
            case "life":
                insurance = new LifeInsurance(base);
                insuranceType = "Life Insurance";
                break;
            case "health":
                insurance = new HealthInsurance(base);
                insuranceType = "Health Insurance";
                break;
            case "car":
                insurance = new CarInsurance(base);
                insuranceType = "Car Insurance";
                break;
        }
        
        double premium = insurance.calculatePremium();
        
        System.out.println("Insurance Type: " + insuranceType);
        System.out.println("Premium: " + premium);
        
        sc.close();
    }
}
