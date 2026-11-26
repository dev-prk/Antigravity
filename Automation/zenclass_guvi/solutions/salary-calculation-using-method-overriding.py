class Employee:
    def calculateSalary(self, basic_salary):
        return basic_salary

class Manager(Employee):
    def calculateSalary(self, basic_salary):
        return super().calculateSalary(basic_salary) + 5000

if __name__ == "__main__":
    basic_salary = int(input().strip())
    emp = Employee()
    mgr = Manager()
    print(f"Employee Salary: {emp.calculateSalary(basic_salary)}")
    print(f"Manager Salary: {mgr.calculateSalary(basic_salary)}")
