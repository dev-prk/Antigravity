#include <iostream>
#include <iomanip>

class BankAccount {
private:
    double principal;
public:
    BankAccount(double p) : principal(p) {}
    
    double calculateInterest(double rate, double time) const {
        return (principal * rate * time) / 100.0;
    }
};

int main() {
    double principal, rate, time;
    std::cin >> principal >> rate >> time;
    
    const BankAccount account(principal);
    double interest = account.calculateInterest(rate, time);
    
    // Check if interest is effectively an integer
    if (interest == static_cast<long long>(interest)) {
        std::cout << static_cast<long long>(interest) << std::endl;
    } else {
        std::cout << interest << std::endl;
    }
    
    return 0;
}
