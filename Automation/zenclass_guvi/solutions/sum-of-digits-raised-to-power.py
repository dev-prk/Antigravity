import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print(0)
        return
    num_digits = len(line)
    total = sum(int(d) ** num_digits for d in line)
    print(total)

if __name__ == "__main__":
    main()
