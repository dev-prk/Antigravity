import java.util.Scanner;

abstract class Ticket {
    protected int distance;
    
    public Ticket(int distance) {
        this.distance = distance;
    }
    
    public abstract int calculateFare();
}

class BusTicket extends Ticket {
    public BusTicket(int distance) {
        super(distance);
    }
    
    @Override
    public int calculateFare() {
        return distance * 5;
    }
}

class TrainTicket extends Ticket {
    public TrainTicket(int distance) {
        super(distance);
    }
    
    @Override
    public int calculateFare() {
        return distance * 8;
    }
}

class FlightTicket extends Ticket {
    public FlightTicket(int distance) {
        super(distance);
    }
    
    @Override
    public int calculateFare() {
        return distance * 15;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        String ticketType = sc.nextLine().trim();
        int distance = sc.nextInt();
        
        Ticket ticket = null;
        String outputType = "";
        
        switch (ticketType.toLowerCase()) {
            case "bus":
                ticket = new BusTicket(distance);
                outputType = "Bus Ticket";
                break;
            case "train":
                ticket = new TrainTicket(distance);
                outputType = "Train Ticket";
                break;
            case "flight":
                ticket = new FlightTicket(distance);
                outputType = "Flight Ticket";
                break;
        }
        
        System.out.println("Ticket Type: " + outputType);
        System.out.println("Fare: " + ticket.calculateFare());
    }
}
