import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    it = iter(data)
    n = int(next(it))
    employees = {}
    
    for _ in range(n):
        emp_id = int(next(it))
        name = next(it)          # name is not used further
        salary = int(next(it))
        employees[emp_id] = salary
    
    try:
        update_id = int(next(it))
        new_salary = int(next(it))
    except StopIteration:
        return
    
    if update_id in employees:
        employees[update_id] = new_salary
        print("Salary updated successfully")
    else:
        print("Employee not found")

if __name__ == "__main__":
    main()
