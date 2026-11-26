import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    age = int(line)
    if age >= 18:
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
