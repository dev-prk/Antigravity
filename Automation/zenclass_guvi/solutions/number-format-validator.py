import sys

def main():
    s = sys.stdin.readline()
    if s == "":
        print("Error: Invalid number format")
        return
    s = s.strip()
    try:
        print(int(s))
    except ValueError:
        print("Error: Invalid number format")

if __name__ == "__main__":
    main()
