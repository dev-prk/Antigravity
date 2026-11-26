import sys

def main():
    data = sys.stdin.read().strip().splitlines()
    if not data:
        return
    
    n = int(data[0].strip())
    employees = []
    
    for i in range(1, n + 1):
        if i >= len(data):
            break
        line = data[i].strip()
        if not line:
            continue
        parts = line.split()
        emp_id = parts[0]
        salary_per_hour = int(parts[-2])
        working_hours = int(parts[-1])
        name = parts[1]
        role = ' '.join(parts[2:-2])
        
        salary = salary_per_hour * working_hours
        employees.append((emp_id, name, role, salary))
    
    for i, (emp_id, name, role, salary) in enumerate(employees):
        if i > 0:
            print()
        print(emp_id)
        print(name)
        print(role)
        print(salary)

if __name__ == "__main__":
    main()
