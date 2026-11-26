#include <iostream>
using namespace std;

class SecureWallet {
private:
    int balance;
public:
    explicit SecureWallet(int b) {
        if (b < 0) {
            cout << "Invalid Balance" << endl;
            exit(0);
        }
        balance = b;
    }
    
    SecureWallet operator+(const SecureWallet& other) {
        SecureWallet result(0);
        result.balance = this->balance + other.balance;
        return result;
    }
    
    int getBalance() const {
        return balance;
    }
};

int main() {
    int initialBalance;
    cin >> initialBalance;
    
    SecureWallet wallet1(initialBalance);
    SecureWallet wallet2(initialBalance);
    
    SecureWallet total = wallet1 + wallet2;
    
    cout << "Total Balance: " << total.getBalance() << endl;
    
    return 0;
}
