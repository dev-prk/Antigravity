import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    a, b = int(data[0]), int(data[1])
    xor_val = a ^ b
    count = bin(xor_val).count('1')
    print(count)

if __name__ == "__main__":
    main()
