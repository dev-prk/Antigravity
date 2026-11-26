#include <iostream>
#include <iomanip>
using namespace std;

class Payment {
protected:
    double amount;
public:
    Payment(double amt) : amount(amt) {}
    double getAmount() {
        return amount;
    }
    virtual double calculateFinalAmount() = 0;
    virtual ~Payment() {}
};

class CreditCard : public Payment {
public:
    CreditCard(double amt) : Payment(amt) {}
    double calculateFinalAmount() override {
        return amount + (0.02 * amount);
    }
};

class UPI : public Payment {
public:
    UPI(double amt) : Payment(amt) {}
    double calculateFinalAmount() override {
        return amount + (0.005 * amount);
    }
};

class NetBanking : public Payment {
public:
    NetBanking(double amt) : Payment(amt) {}
    double calculateFinalAmount() override {
        return amount + 10;
    }
};

int main() {
    int N;
    cin >> N;
    double total = 0;
    
    for (int i = 0; i < N; i++) {
        int type;
        double amt;
        cin >> type >> amt;
        
        Payment* payment = nullptr;
        
        switch (type) {
            case 1:
                payment = new CreditCard(amt);
                break;
            case 2:
                payment = new UPI(amt);
                break;
            case 3:
                payment = new NetBanking(amt);
                break;
        }
        
        double finalAmt = payment->calculateFinalAmount();
        total += finalAmt;
        
        cout << fixed << setprecision(2);
        cout << "Final Amount: " << finalAmt << endl;
        
        delete payment;
    }
    
    cout << "Total Processed Amount: " << total << endl;
    
    return 0;
}
