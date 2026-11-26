import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print("no")
        return
    try:
        n = int(line)
    except ValueError:
        print("no")
        return
    
    if n <= 0:
        print("no")
    elif n & (n - 1) == 0:
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
