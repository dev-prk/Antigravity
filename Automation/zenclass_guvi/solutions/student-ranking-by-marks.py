import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    students = []
    
    index = 1
    for i in range(n):
        student_id = data[index]
        cs_marks = int(data[index + 1])
        maths_marks = int(data[index + 2])
        english_marks = int(data[index + 3])
        students.append((student_id, cs_marks, maths_marks, english_marks))
        index += 4
    
    students.sort(key=lambda x: (-x[2], -x[1], -x[3]))
    
    for student in students:
        print(f"{student[0]} {student[1]} {student[2]} {student[3]}")

if __name__ == "__main__":
    main()
