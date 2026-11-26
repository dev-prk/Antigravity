import sys

class Student:
    def __init__(self, sid, name, marks):
        self.id = sid
        self.name = name
        self.marks = marks

    def grade(self):
        if self.marks >= 90:
            return 'A'
        elif self.marks >= 75:
            return 'B'
        elif self.marks >= 50:
            return 'C'
        else:
            return 'D'

def main():
    data = sys.stdin.read().splitlines()
    sid = data[0].strip()
    name = data[1].strip()
    marks = int(data[2].strip())
    s = Student(sid, name, marks)
    print(f"Student ID: {s.id}")
    print(f"Student Name: {s.name}")
    print(f"Marks: {s.marks}")
    print(f"Grade: {s.grade()}")

if __name__ == "__main__":
    main()
