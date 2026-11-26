import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print(0)
        return
    parts = line.split()
    num1 = int(parts[0])
    num2 = int(parts[1])
    
    count = 0
    for digit in str(num1):
        if int(digit) == num2:
            count += 1
    print(count)

if __name__ == "__main__":
    main()
