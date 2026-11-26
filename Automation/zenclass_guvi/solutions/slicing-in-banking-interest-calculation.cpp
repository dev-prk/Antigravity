#include <iostream>
#include <vector>

class Account {
protected:
    double balance;
public:
    Account(double b) : balance(b) {}
    virtual double calculateInterest() {
        return 0.0;
    }
    virtual ~Account() {}
};

class FixedDeposit : public Account {
private:
    double interestRate;
public:
    FixedDeposit(double b, double rate) : Account(b), interestRate(rate) {}
    double calculateInterest() override {
        return balance * interestRate / 100.0;
    }
};

int main() {
    double balance, rate;
    std::cin >> balance >> rate;
    
    FixedDeposit fd(balance, rate);
    
    std::vector<Account> accounts;
    accounts.push_back(fd);
    
    std::cout << "Interest (Sliced): " << (int)accounts[0].calculateInterest() << std::endl;
    
    Account* accPtr = &fd;
    std::cout << "Interest (Correct): " << (int)accPtr->calculateInterest() << std::endl;
    
    return 0;
}
