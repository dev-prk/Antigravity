import sys
import math

class Shape:
    def area(self):
        pass
    
    def perimeter(self):
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return math.pi * self.radius ** 2
    
    def perimeter(self):
        return 2 * math.pi * self.radius

class Rectangle(Shape):
    def __init__(self, length, width):
        self.length = length
        self.width = width
    
    def area(self):
        return self.length * self.width
    
    def perimeter(self):
        return 2 * (self.length + self.width)

class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
    
    def area(self):
        s = (self.a + self.b + self.c) / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))
    
    def perimeter(self):
        return self.a + self.b + self.c

def main():
    while True:
        shape_input = sys.stdin.readline().strip()
        if shape_input == "quit":
            print("Quitting the program.")
            break
        
        if shape_input == "circle":
            radius_line = sys.stdin.readline().strip()
            try:
                radius = float(radius_line)
                circle = Circle(radius)
                print(f"Area of the circle: {circle.area():.2f}")
                print(f"Perimeter of the circle: {circle.perimeter():.2f}")
            except:
                print("Invalid input. Please enter a valid shape (circle/rectangle/triangle).")
        
        elif shape_input == "rectangle":
            rect_line = sys.stdin.readline().strip()
            try:
                parts = rect_line.split()
                length = float(parts[0])
                width = float(parts[1])
                rectangle = Rectangle(length, width)
                print(f"Area of the rectangle: {rectangle.area():.2f}")
                print(f"Perimeter of the rectangle: {rectangle.perimeter():.2f}")
            except:
                print("Invalid input. Please enter a valid shape (circle/rectangle/triangle).")
        
        elif shape_input == "triangle":
            tri_line = sys.stdin.readline().strip()
            try:
                parts = tri_line.split()
                a = float(parts[0])
                b = float(parts[1])
                c = float(parts[2])
                triangle = Triangle(a, b, c)
                print(f"Area of the triangle: {triangle.area():.2f}")
                print(f"Perimeter of the triangle: {triangle.perimeter():.2f}")
            except:
                print("Invalid input. Please enter a valid shape (circle/rectangle/triangle).")
        
        else:
            print("Invalid input. Please enter a valid shape (circle/rectangle/triangle).")

if __name__ == "__main__":
    main()
