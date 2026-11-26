import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print(0)
        return
    product = 1
    for char in line:
        digit = int(char)
        product *= digit
    print(product)

if __name__ == "__main__":
    main()
