import java.util.*;
import java.io.*;

class TicketCounter {
    private int availableSeats;
    
    public TicketCounter(int totalSeats) {
        this.availableSeats = totalSeats;
    }
    
    public synchronized boolean bookSeats(int tickets, int userId) {
        if (tickets <= availableSeats) {
            availableSeats -= tickets;
            System.out.println("User" + userId + " booked " + tickets + " tickets.");
            return true;
        } else {
            System.out.println("User" + userId + " could not book (only " + availableSeats + " left).");
            return false;
        }
    }
    
    public int getRemainingSeats() {
        return availableSeats;
    }
}

class BookingThread extends Thread {
    private TicketCounter counter;
    private int tickets;
    private int userId;
    
    public BookingThread(TicketCounter counter, int tickets, int userId) {
        this.counter = counter;
        this.tickets = tickets;
        this.userId = userId;
    }
    
    @Override
    public void run() {
        counter.bookSeats(tickets, userId);
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int totalSeats = sc.nextInt();
        int numRequests = sc.nextInt();
        
        TicketCounter counter = new TicketCounter(totalSeats);
        ArrayList<BookingThread> threads = new ArrayList<>();
        
        for (int i = 1; i <= numRequests; i++) {
            int tickets = sc.nextInt();
            BookingThread thread = new BookingThread(counter, tickets, i);
            threads.add(thread);
        }
        
        for (BookingThread thread : threads) {
            thread.start();
        }
        
        for (BookingThread thread : threads) {
            try {
                thread.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        
        System.out.println("Remaining Seats: " + counter.getRemainingSeats());
        
        sc.close();
    }
}
