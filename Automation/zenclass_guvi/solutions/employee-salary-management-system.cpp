#include <iostream>
#include <vector>
#include <string>
#include <iomanip>

class Employee {
private:
    std::string name;
    int id;
    double baseSalary;

public:
    Employee(const std::string& n, int i, double bs) : name(n), id(i), baseSalary(bs) {}
    
    virtual ~Employee() = default;
    
    double getBaseSalary() const { return baseSalary; }
    std::string getName() const { return name; }
    int getId() const { return id; }
    
    virtual double calculateSalary() = 0;
};

class FullTimeEmployee : public Employee {
public:
    FullTimeEmployee(const std::string& n, int i, double bs) : Employee(n, i, bs) {}
    
    double calculateSalary() override {
        return getBaseSalary() * 1.2;
    }
};

class PartTimeEmployee : public Employee {
public:
    PartTimeEmployee(const std::string& n, int i, double bs) : Employee(n, i, bs) {}
    
    double calculateSalary() override {
        return getBaseSalary();
    }
};

int main() {
    int type;
    std::string name;
    int id;
    double baseSalary;
    
    while (std::cin >> type >> name >> id >> baseSalary) {
        Employee* emp = nullptr;
        
        if (type == 1) {
            emp = new FullTimeEmployee(name, id, baseSalary);
        } else if (type == 2) {
            emp = new PartTimeEmployee(name, id, baseSalary);
        }
        
        if (emp) {
            std::cout << "Employee Name: " << emp->getName() << "\n";
            std::cout << "Employee ID: " << emp->getId() << "\n";
            std::cout << std::fixed << std::setprecision(2);
            std::cout << "Final Salary: " << emp->calculateSalary() << "\n";
            delete emp;
        }
    }
    
    return 0;
}
