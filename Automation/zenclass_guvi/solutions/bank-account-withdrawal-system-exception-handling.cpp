#include <iostream>
#include <string>
using namespace std;

class BankAccount {
private:
    double balance;
public:
    BankAccount(double initialBalance) {
        if (initialBalance < 0) {
            throw string("Invalid initial balance");
        }
        balance = initialBalance;
    }
    
    void withdraw(double amount) {
        if (amount <= 0) {
            throw string("Invalid withdrawal amount");
        }
        if (amount > balance) {
            throw string("Insufficient balance");
        }
        balance -= amount;
        cout << "Withdrawal successful" << endl;
        cout << "Remaining balance: " << balance << endl;
    }
};

int main() {
    double initialBalance, withdrawAmount;
    
    cin >> initialBalance;
    cin >> withdrawAmount;
    
    try {
        BankAccount account(initialBalance);
        account.withdraw(withdrawAmount);
    } catch (const string& e) {
        cout << e << endl;
    }
    
    return 0;
}
