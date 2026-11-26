from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, length, breadth):
        self.length = length
        self.breadth = breadth
    
    def area(self):
        return self.length * self.breadth

length = int(input())
breadth = int(input())
rect = Rectangle(length, breadth)
print(f"Area of Rectangle: {rect.area()}")
