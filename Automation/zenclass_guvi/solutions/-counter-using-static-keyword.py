class Employee:
    count = 0
    
    def __init__(self):
        Employee.count += 1

n = int(input())
employees = []
for _ in range(n):
    employees.append(Employee())

print(f"Total Employee Objects Created: {n}")
print(f"Static Counter Value: {Employee.count}")
