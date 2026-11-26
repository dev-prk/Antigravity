import sys
from collections import Counter

def main():
    s = sys.stdin.readline().strip()
    target = "dhoni"
    
    if len(s) != len(target):
        print("no")
        return
    
    if Counter(s) == Counter(target):
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
