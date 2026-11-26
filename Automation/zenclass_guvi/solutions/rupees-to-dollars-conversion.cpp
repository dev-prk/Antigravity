#include <iostream>
#include <iomanip>
using namespace std;

class Dollar;

class Rupee {
private:
    double amount;
public:
    Rupee(double r = 0) : amount(r) {}
    
    operator Dollar() const;
    
    double getAmount() const { return amount; }
};

class Dollar {
private:
    double amount;
public:
    Dollar(double d = 0) : amount(d) {}
    
    double getAmount() const { return amount; }
};

Rupee::operator Dollar() const {
    return Dollar(amount / 83.0);
}

int main() {
    double rupees;
    cin >> rupees;
    
    Rupee r(rupees);
    Dollar d = r;
    
    cout << fixed << setprecision(2) << d.getAmount() << endl;
    
    return 0;
}
