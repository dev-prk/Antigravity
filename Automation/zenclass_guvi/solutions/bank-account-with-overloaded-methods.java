import java.util.Scanner;

class BankAccount {
    private double balance;
    
    public BankAccount(double initialBalance) {
        this.balance = initialBalance;
    }
    
    public void deposit(int amount) {
        balance += (double) amount;
    }
    
    public void deposit(double amount) {
        balance += amount;
    }
    
    public double getBalance() {
        return balance;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        double initialBalance = sc.nextDouble();
        BankAccount account = new BankAccount(initialBalance);
        
        int numberOfDeposits = sc.nextInt();
        
        for (int i = 0; i < numberOfDeposits; i++) {
            if (sc.hasNextDouble()) {
                double deposit = sc.nextDouble();
                if (deposit == (int) deposit) {
                    account.deposit((int) deposit);
                } else {
                    account.deposit(deposit);
                }
            }
        }
        
        System.out.println("Total Balance: " + (int) account.getBalance());
        sc.close();
    }
}
