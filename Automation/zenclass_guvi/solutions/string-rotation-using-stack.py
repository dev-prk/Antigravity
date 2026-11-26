import sys

def main():
    s1 = sys.stdin.readline().rstrip('\n')
    s2 = sys.stdin.readline().rstrip('\n')
    
    if len(s1) != len(s2):
        print(0)
        return
    
    n = len(s1)
    if n == 0:
        print(1)
        return
    
    # Rotate s1 by 2 places clockwise (right rotation)
    # Right rotation by 2: last 2 chars move to front
    rotated = s1[-2:] + s1[:-2]
    
    if rotated == s2:
        print(1)
    else:
        print(0)

if __name__ == "__main__":
    main()
