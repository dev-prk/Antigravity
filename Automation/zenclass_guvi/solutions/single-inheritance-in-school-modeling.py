import sys

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

class Student(Person):
    def __init__(self, name, age, department):
        super().__init__(name, age)
        self.department = department
    
    def print_details(self):
        print(f"Student: {self.name}, Age: {self.age}, Department: {self.department}")

class Teacher(Person):
    def __init__(self, name, age, subject):
        super().__init__(name, age)
        self.subject = subject
    
    def print_details(self):
        print(f"Teacher: {self.name}, Age: {self.age}, Subject: {self.subject}")

def main():
    lines = sys.stdin.read().strip().split('\n')
    for line in lines:
        if not line.strip():
            continue
        parts = line.split(', ')
        name = parts[0].strip()
        age = int(parts[1].strip())
        category = parts[2].strip()
        
        if line.startswith('Dr.') or line.startswith('Prof.') or 'Professor' in category or 'Prof' in name or 'Dr' in name:
            teacher = Teacher(name, age, category)
            teacher.print_details()
        else:
            student = Student(name, age, category)
            student.print_details()

if __name__ == "__main__":
    main()
