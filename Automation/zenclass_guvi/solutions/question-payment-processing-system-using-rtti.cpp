#include <iostream>
#include <typeinfo>
#include <string>

class Payment {
public:
    virtual ~Payment() {}
    virtual double processPayment() const = 0;
};

class CreditCard : public Payment {
private:
    double amount;
public:
    CreditCard(double amt) : amount(amt) {}
    double processPayment() const override {
        return amount * 1.02;
    }
};

class UPI : public Payment {
private:
    double amount;
public:
    UPI(double amt) : amount(amt) {}
    double processPayment() const override {
        return amount;
    }
};

class NetBanking : public Payment {
private:
    double amount;
public:
    NetBanking(double amt) : amount(amt) {}
    double processPayment() const override {
        return amount * 1.01;
    }
};

void identifyPayment(Payment* p) {
    if (dynamic_cast<CreditCard*>(p)) {
        std::cout << "Type: CreditCard" << std::endl;
        std::cout << "Final Amount: " << static_cast<CreditCard*>(p)->processPayment() << std::endl;
    } else if (dynamic_cast<UPI*>(p)) {
        std::cout << "Type: UPI" << std::endl;
        std::cout << "Final Amount: " << static_cast<UPI*>(p)->processPayment() << std::endl;
    } else if (dynamic_cast<NetBanking*>(p)) {
        std::cout << "Type: NetBanking" << std::endl;
        std::cout << "Final Amount: " << static_cast<NetBanking*>(p)->processPayment() << std::endl;
    } else {
        std::cout << "Invalid Payment Method" << std::endl;
    }
}

int main() {
    int n;
    std::cin >> n;
    Payment* payments[n];
    
    for (int i = 0; i < n; i++) {
        char method;
        double amount;
        std::cin >> method >> amount;
        
        switch (method) {
            case 'C':
                payments[i] = new CreditCard(amount);
                break;
            case 'U':
                payments[i] = new UPI(amount);
                break;
            case 'N':
                payments[i] = new NetBanking(amount);
                break;
            default:
                payments[i] = nullptr;
                break;
        }
    }
    
    for (int i = 0; i < n; i++) {
        identifyPayment(payments[i]);
        delete payments[i];
    }
    
    return 0;
}
