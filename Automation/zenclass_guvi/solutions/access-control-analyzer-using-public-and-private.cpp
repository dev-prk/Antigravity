#include <iostream>
#include <string>
using namespace std;

class Account {
public:
    int accountNumber;
protected:
    double balance;
private:
    int pin;
public:
    void setAccount(int accNum, double bal, int p) {
        accountNumber = accNum;
        balance = bal;
        pin = p;
    }
};

class SavingsAccount : public Account {
public:
    void display() {
        cout << "Savings Account: " << accountNumber << " " << balance << endl;
    }
};

class SecureAccount : private Account {
public:
    void display() {
        cout << "Secure Account: Access Restricted" << endl;
    }
};

int main() {
    int accNum, pin;
    double bal;
    cin >> accNum >> bal >> pin;
    
    SavingsAccount sav;
    SecureAccount sec;
    
    sav.setAccount(accNum, bal, pin);
    // sec.setAccount(accNum, bal, pin); // Can't access due to private inheritance
    
    sav.display();
    sec.display();
    
    return 0;
}
