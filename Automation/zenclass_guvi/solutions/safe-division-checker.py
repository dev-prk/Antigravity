import sys

def main():
    lines = sys.stdin.read().strip().splitlines()
    a = int(lines[0].strip())
    b = int(lines[1].strip())
    try:
        print(a // b)
    except ZeroDivisionError:
        print("Error: Division by zero not allowed")

if __name__ == "__main__":
    main()
