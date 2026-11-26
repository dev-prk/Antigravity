import sys

def main():
    s = sys.stdin.read().strip()
    balance = 0
    for ch in s:
        if ch == '(':
            balance += 1
        elif ch == ')':
            balance -= 1
            if balance < 0:
                print("no")
                return
    print("yes" if balance == 0 else "no")

if __name__ == "__main__":
    main()
