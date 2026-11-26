import sys

class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def display(self):
        print(f"Name: {self.name}")
        print(f"Age: {self.age}")

def main():
    data = sys.stdin.read().strip().splitlines()
    if not data:
        return
    name = data[0].strip()
    age = int(data[1].strip())
    student = Student(name, age)
    student.display()

if __name__ == "__main__":
    main()
