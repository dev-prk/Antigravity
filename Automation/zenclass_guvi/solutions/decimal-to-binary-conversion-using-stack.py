import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    n = int(line)
    if n == 0:
        print("0")
        return
    stack = []
    while n > 0:
        stack.append(n % 2)
        n //= 2
    result = ''.join(str(bit) for bit in stack[::-1])
    print(result)

if __name__ == "__main__":
    main()
