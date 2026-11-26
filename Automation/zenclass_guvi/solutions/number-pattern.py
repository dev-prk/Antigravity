import sys

def main():
    n = int(sys.stdin.readline().strip())
    if n <= 0:
        return
    
    for i in range(n):
        start_num = 2 * i + 1
        numbers = []
        for j in range(i + 1):
            num = start_num - j
            numbers.append(str(num))
        line = " ".join(numbers)
        padding = " " * (2 * (n - i - 1))
        print(padding + line)

if __name__ == "__main__":
    main()
