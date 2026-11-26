import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("No students found")
        return
    
    n = int(data[0])
    students = []
    idx = 1
    
    for _ in range(n):
        if idx + 2 >= len(data):
            break
        sid = data[idx]
        name = data[idx + 1]
        marks = int(data[idx + 2])
        students.append((sid, name, marks))
        idx += 3
    
    if idx >= len(data):
        print("No students found")
        return
    
    min_marks = int(data[idx])
    
    result = []
    for sid, name, marks in students:
        if marks >= min_marks:
            result.append((sid, name, marks))
    
    if not result:
        print("No students found")
    else:
        for sid, name, marks in result:
            print(f"ID: {sid}, Name: {name}, Marks: {marks}")

if __name__ == "__main__":
    main()
