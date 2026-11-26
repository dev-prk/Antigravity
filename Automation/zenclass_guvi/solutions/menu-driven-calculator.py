import sys

def main():
    for line in sys.stdin:
        choice = int(line.strip())
        if choice == 1:
            a = int(sys.stdin.readline().strip())
            b = int(sys.stdin.readline().strip())
            print(a + b)
        elif choice == 2:
            a = int(sys.stdin.readline().strip())
            b = int(sys.stdin.readline().strip())
            print(a - b)
        elif choice == 3:
            a = int(sys.stdin.readline().strip())
            b = int(sys.stdin.readline().strip())
            print(a * b)
        elif choice == 4:
            print("Exit")
            break
        else:
            print("Invalid Choice")

if __name__ == "__main__":
    main()
