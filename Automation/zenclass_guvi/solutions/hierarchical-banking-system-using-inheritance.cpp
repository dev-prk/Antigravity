#include <iostream>

class Account {
protected:
    long long accountNumber;
    long long balance;
public:
    Account(long long acc, long long bal) : accountNumber(acc), balance(bal) {}
    virtual void deposit(long long amt) { balance += amt; }
    virtual void withdraw(long long amt) { balance -= amt; }
    long long getBalance() const { return balance; }
};

class SavingsAccount : public Account {
    double interestRate;
public:
    SavingsAccount(long long acc, long long bal, double rate)
        : Account(acc, bal), interestRate(rate) {}
    // use base withdraw behavior
};

class CurrentAccount : public Account {
    long long overdraftLimit;
public:
    CurrentAccount(long long acc, long long bal, long long limit)
        : Account(acc, bal), overdraftLimit(limit) {}
    void withdraw(long long amt) override {
        balance -= amt;
    }
    long long getOverdraftLimit() const { return overdraftLimit; }
};

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    
    long long accNum, initBal, interestRateInt, overdraftLimit, withdrawAmt;
    if (!(std::cin >> accNum >> initBal >> interestRateInt >> overdraftLimit >> withdrawAmt))
        return 0;
    
    SavingsAccount sav(accNum, initBal, static_cast<double>(interestRateInt));
    CurrentAccount cur(accNum, initBal, overdraftLimit);
    
    // Savings calculation
    long long savNewBal = sav.getBalance() - withdrawAmt;
    if (savNewBal < 0) {
        std::cout << "Savings Balance: " << savNewBal << " not allowed\n";
    } else {
        std::cout << "Savings Balance: " << savNewBal << "\n";
    }
    
    // Current calculation
    long long curNewBal = cur.getBalance() - withdrawAmt;
    if (curNewBal < -cur.getOverdraftLimit()) {
        std::cout << "Current Balance: " << curNewBal << " exceeds overdraft limit\n";
    } else {
        std::cout << "Current Balance: " << curNewBal << "\n";
    }
    
    return 0;
}
