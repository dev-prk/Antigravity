import sys

def main():
    data = sys.stdin.read().strip().split('\n')
    if not data:
        return
    
    idx = 0
    n = int(data[idx])
    idx += 1
    
    students = []
    
    for _ in range(n):
        if idx >= len(data):
            break
        parts = data[idx].split()
        idx += 1
        if len(parts) >= 3:
            reg_num = int(parts[0])
            name = parts[1]
            marks = int(parts[2])
            students.append((reg_num, name, marks))
    
    k = int(data[idx])
    idx += 1
    
    for _ in range(k):
        if idx >= len(data):
            break
        parts = data[idx].split()
        idx += 1
        if len(parts) >= 3:
            reg_num = int(parts[0])
            name = parts[1]
            marks = int(parts[2])
            students.append((reg_num, name, marks))
    
    total_students = len(students)
    
    total_marks = sum(s[2] for s in students)
    average = total_marks / total_students if total_students > 0 else 0.0
    
    topper = max(students, key=lambda s: s[2])
    
    print(f"Total Students: {total_students}")
    print(f"Average Marks: {average:.2f}")
    print(f"Topper: {topper[1]}")
    print(f"Register Number: {topper[0]}")
    print(f"Marks: {topper[2]}")

if __name__ == "__main__":
    main()
