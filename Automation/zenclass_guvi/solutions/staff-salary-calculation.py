import sys
from abc import ABC, abstractmethod

class StaffMember(ABC):
    @abstractmethod
    def get_salary(self):
        pass

class Teacher(StaffMember):
    def get_salary(self):
        return 3000

class Janitor(StaffMember):
    def get_salary(self):
        return 2000

class Administrator(StaffMember):
    def get_salary(self):
        return 4000

for line in sys.stdin:
    line = line.strip()
    if line:
        result = eval(line)
        print(result)
