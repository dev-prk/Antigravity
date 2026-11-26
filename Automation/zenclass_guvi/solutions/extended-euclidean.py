import sys

def extended_gcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return (g, x, y)

def main():
    line = sys.stdin.readline().strip()
    if '=' in line:
        parts = line.split(',')
        a = int(parts[0].split('=')[1])
        b = int(parts[1].split('=')[1])
    else:
        parts = line.split()
        a = int(parts[0])
        b = int(parts[1])
    
    g, x, y = extended_gcd(a, b)
    print(f"{x} {y}")

if __name__ == "__main__":
    main()
