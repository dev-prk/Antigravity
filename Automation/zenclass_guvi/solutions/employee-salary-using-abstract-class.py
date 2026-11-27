import sys
from abc import ABC, abstractmethod

class Employee(ABC):
    def __init__(self, name):
        self.name = name
    
    @abstractmethod
    def calculateSalary(self):
        pass

class FullTimeEmployee(Employee):
    def __init__(self, name, monthly_salary):
        super().__init__(name)
        self.monthly_salary = monthly_salary
    
    def calculateSalary(self):
        return self.monthly_salary

class PartTimeEmployee(Employee):
    def __init__(self, name, hourly_rate, hours):
        super().__init__(name)
        self.hourly_rate = hourly_rate
        self.hours = hours
    
    def calculateSalary(self):
        return self.hourly_rate * self.hours

def main():
    data = sys.stdin.read().split()
    if not data:
        print(-1)
        return
    
    employee_type = data[0]
    
    if employee_type == "fulltime":
        if len(data) < 2:
            print(-1)
            return
        monthly_salary = int(data[1])
        employee = FullTimeEmployee("Employee", monthly_salary)
        print(employee.calculateSalary())
    elif employee_type == "parttime":
        if len(data) < 3:
            print(-1)
            return
        hourly_rate = int(data[1])
        hours = int(data[2])
        employee = PartTimeEmployee("Employee", hourly_rate, hours)
        print(employee.calculateSalary())
    else:
        print(-1)

if __name__ == "__main__":
    main()
