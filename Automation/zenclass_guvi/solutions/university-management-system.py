import sys

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def displayProfile(self):
        print(f"Name: {self.name}")
        print(f"Age: {self.age}")

class Faculty(Person):
    def __init__(self, name, age, department):
        super().__init__(name, age)
        self.department = department
    def displayProfile(self):
        super().displayProfile()
        print(f"Department: {self.department}")

class Professor(Faculty):
    def __init__(self, name, age, department, researchArea):
        super().__init__(name, age, department)
        self.researchArea = researchArea
    def displayProfile(self):
        super().displayProfile()
        print(f"Research Area: {self.researchArea}")

def main():
    lines = [sys.stdin.readline().rstrip('\n') for _ in range(4)]
    name = lines[0]
    age = int(lines[1])
    department = lines[2]
    research = lines[3]
    prof = Professor(name, age, department, research)
    prof.displayProfile()

if __name__ == "__main__":
    main()
