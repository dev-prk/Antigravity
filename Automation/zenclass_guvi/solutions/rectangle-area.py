import sys

class Rectangle:
    def __init__(self, length, width):
        self.length = length
        self.width = width
    
    def calculateArea(self):
        return self.length * self.width

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    length = int(data[0])
    width = int(data[1]) if len(data) > 1 else 0
    rect = Rectangle(length, width)
    print(rect.calculateArea())

if __name__ == "__main__":
    main()
