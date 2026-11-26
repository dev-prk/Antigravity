import sys

def solve():
    data = sys.stdin.read().strip().split()
    a = int(data[0])
    b = int(data[1])
    c = int(data[2])
    
    sides = sorted([a, b, c])
    x, y, z = sides[0], sides[1], sides[2]
    
    if x * x + y * y == z * z:
        print('yes')
    else:
        print('no')

if __name__ == "__main__":
    solve()
