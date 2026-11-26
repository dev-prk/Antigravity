#include <iostream>
#include <iomanip>

class Employee {
private:
    double basicSalary;
    double hraPercent;
    double daPercent;
    double taxPercent;
    double netSalary;

public:
    Employee() {
        std::cin >> basicSalary >> hraPercent >> daPercent >> taxPercent;
        
        double hra = basicSalary * hraPercent / 100.0;
        double da = basicSalary * daPercent / 100.0;
        double grossSalary = basicSalary + hra + da;
        
        double tax = grossSalary * taxPercent / 100.0;
        netSalary = grossSalary - tax;
    }
    
    void display() const {
        std::cout << std::fixed << std::setprecision(2) << netSalary << std::endl;
    }
};

int main() {
    Employee emp;
    emp.display();
    return 0;
}
