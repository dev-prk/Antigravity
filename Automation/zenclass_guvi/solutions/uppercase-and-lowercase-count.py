import sys

def main():
    data = sys.stdin.read()
    if not data:
        return
    lower = sum(1 for ch in data if ch.islower())
    upper = sum(1 for ch in data if ch.isupper())
    print(f"lowercase:{lower}")
    print(f"uppercase:{upper}")

if __name__ == "__main__":
    main()
