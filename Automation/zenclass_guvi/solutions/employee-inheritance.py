import sys

def main():
    lines = sys.stdin.read().splitlines()
    if len(lines) < 3:
        return
    name = lines[0].strip()
    salary_input = lines[1].strip()
    department = lines[2].strip()
    try:
        salary = float(salary_input)
    except:
        salary = 0.0

    class Employee:
        def __init__(self, name, salary):
            self.name = name
            self.salary = salary

    class Manager(Employee):
        def __init__(self, name, salary, department):
            super().__init__(name, salary)
            self.department = department

        def displayDetails(self):
            print(f"Name: {self.name}")
            print(f"Salary: {self.salary}")
            print(f"Department: {self.department}")

    mgr = Manager(name, salary, department)
    mgr.displayDetails()

if __name__ == "__main__":
    main()
