#include <iostream>
#include <string>
#include <iomanip>

class ElectricityBill {
private:
    std::string customerName;
    int unitsConsumed;
    double ratePerUnit;
    double totalBill;

public:
    void setDetails(std::string name, int units) {
        customerName = name;
        unitsConsumed = units;
    }

    void calculateBill(double rate = 5.0) {
        ratePerUnit = rate;
        totalBill = unitsConsumed * ratePerUnit;
    }

    void display() {
        std::cout << "Customer Name: " << customerName << std::endl;
        std::cout << "Units Consumed: " << unitsConsumed << std::endl;
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Rate per Unit: " << ratePerUnit << std::endl;
        std::cout << "Total Bill: " << totalBill << std::endl;
    }
};

int main() {
    std::string customerName;
    int units;
    double rate;

    std::cin >> customerName >> units >> rate;

    ElectricityBill bill;
    bill.setDetails(customerName, units);

    if (rate == 0) {
        bill.calculateBill();  // Uses default rate of 5.0
    } else {
        bill.calculateBill(rate);
    }

    bill.display();

    return 0;
}
