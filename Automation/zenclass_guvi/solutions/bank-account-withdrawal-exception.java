import java.util.Scanner;

// Custom Exception Class
class InsufficientFundsException extends Exception {
    public InsufficientFundsException(String message) {
        super(message);
    }
}

// BankAccount Class
class BankAccount {
    private double balance;

    public BankAccount(double initialBalance) {
        this.balance = initialBalance;
    }

    public void withdraw(double amount) throws InsufficientFundsException {
        if (amount > balance) {
            throw new InsufficientFundsException("Withdrawal exceeds balance.");
        }
        balance -= amount;
    }

    public double getBalance() {
        return balance;
    }
}

// Main Class
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        double balance = sc.nextDouble();
        double withdrawal = sc.nextDouble();
        BankAccount account = new BankAccount(balance);
        try {
            account.withdraw(withdrawal);
            System.out.println("Withdrawal successful. Remaining balance: " + account.getBalance());
        } catch (InsufficientFundsException e) {
            System.out.println("Insufficient funds: " + e.getMessage());
        }
    }
}
