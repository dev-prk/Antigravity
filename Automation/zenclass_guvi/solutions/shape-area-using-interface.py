import sys

class Shape:
    def Area(self):
        raise NotImplementedError

class Rectangle(Shape):
    def __init__(self, length, width):
        self.length = length
        self.width = width
    
    def Area(self):
        return self.length * self.width

class Square(Shape):
    def __init__(self, side):
        self.side = side
    
    def Area(self):
        return self.side * self.side

def main():
    lines = sys.stdin.read().strip().split("\n")
    if not lines:
        return
    
    shape_type = lines[0].strip().lower()
    params_str = lines[1].strip()
    params = list(map(float, params_str.split()))
    
    if shape_type == "rectangle":
        length = params[0]
        width = params[1]
        shape = Rectangle(length, width)
    elif shape_type == "square":
        side = params[0]
        shape = Square(side)
    else:
        return
        
    area = shape.Area()
    
    if area == int(area):
        print(int(area))
    else:
        print(area)

if __name__ == "__main__":
    main()
