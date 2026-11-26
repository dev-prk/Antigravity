import sys

class Triangle:
    def __init__(self):
        pass

def main():
    lines = sys.stdin.read().strip().split()
    base = int(lines[0])
    height = int(lines[1])
    
    triangle = Triangle()
    area = (base * height) // 2
    print(area)

if __name__ == "__main__":
    main()
