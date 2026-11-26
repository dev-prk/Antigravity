import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("Employee not found")
        return
    
    n = int(data[0])
    employees = {}
    idx = 1
    
    for _ in range(n):
        emp_id = int(data[idx])
        name = data[idx + 1]
        salary = int(data[idx + 2])
        employees[emp_id] = (name, salary)
        idx += 3
    
    search_id = int(data[idx])
    
    if search_id in employees:
        name, salary = employees[search_id]
        print(f"Name: {name}")
        print(f"Salary: {float(salary)}")
    else:
        print("Employee not found")

if __name__ == "__main__":
    main()
