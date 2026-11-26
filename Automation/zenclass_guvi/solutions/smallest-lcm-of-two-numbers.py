import sys, math

def main():
    data = sys.stdin.read().split()
    L = int(data[0])
    R = int(data[1])
    g = math.gcd(L, R)
    lcm = L // g * R
    print(lcm)

if __name__ == "__main__":
    main()
