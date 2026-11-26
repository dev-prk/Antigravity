import math

class Circle:
    def __init__(self):
        pass
    
    def area(self, r):
        return math.pi * r * r
    
    def circumference(self, r):
        return 2 * math.pi * r

def main():
    r = int(input().strip())
    c = Circle()
    print(round(c.area(r), 1))
    print(round(c.circumference(r), 1))

if __name__ == "__main__":
    main()
