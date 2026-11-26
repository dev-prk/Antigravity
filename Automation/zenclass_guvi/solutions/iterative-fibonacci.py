import sys

def main():
    line = sys.stdin.readline().strip()
    if '=' in line:
        n = int(line.split('=')[1])
    else:
        n = int(line)
    
    if n == 0:
        print(0)
    elif n == 1:
        print(1)
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        print(b)

if __name__ == "__main__":
    main()
