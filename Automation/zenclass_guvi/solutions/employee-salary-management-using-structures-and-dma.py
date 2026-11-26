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
        if len(parts) >= 3:
            emp_id = int(parts[0])
            salary = int(parts[-1])
            name = ' '.join(parts[1:-1])
            employees.append((emp_id, name, salary))
    
    if employees:
        max_emp = max(employees, key=lambda x: x[2])
        print(f"Employee ID: {max_emp[0]}")
        print(f"Employee Name: {max_emp[1]}")
        print(f"Salary: {float(max_emp[2]):.2f}")

if __name__ == "__main__":
    main()
