#include <iostream>

class Employee {
public:
    void processSalary(int baseSalary) {
        int bonus = calculateBonus(baseSalary);
        int total = baseSalary + bonus;
        displayTotal(total);
    }

protected:
    int calculateBonus(int baseSalary) {
        return static_cast<int>(baseSalary * 0.2);
    }

private:
    void displayTotal(int totalSalary) {
        std::cout << "Total Salary: " << totalSalary << std::endl;
    }
};

class SecureEmployee : private Employee {
public:
    void generateSalary(int baseSalary) {
        if (baseSalary <= 0) {
            std::cout << "Invalid Salary" << std::endl;
            return;
        }
        processSalary(baseSalary);
    }
};

int main() {
    int salary;
    std::cin >> salary;
    
    SecureEmployee emp;
    emp.generateSalary(salary);
    
    return 0;
}
