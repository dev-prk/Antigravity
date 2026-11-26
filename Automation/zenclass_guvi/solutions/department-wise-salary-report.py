import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    
    n = int(data[0])
    index = 1
    
    departments = {}
    
    for _ in range(n):
        emp_id = int(data[index])
        name = data[index + 1]
        dept = data[index + 2]
        salary = int(data[index + 3])
        index += 4
        
        if dept not in departments:
            departments[dept] = []
        departments[dept].append(salary)
    
    query_dept = data[index]
    
    if query_dept not in departments:
        print("Department not found")
        return
    
    salaries = departments[query_dept]
    count = len(salaries)
    total = sum(salaries)
    average = total / count
    maximum = max(salaries)
    
    print(f"Department: {query_dept}")
    print(f"Employee Count: {count}")
    print(f"Total Salary: {float(total)}")
    print(f"Average Salary: {average:.2f}")
    print(f"Maximum Salary: {float(maximum)}")

if __name__ == "__main__":
    main()
