import sys

def solve():
    s = sys.stdin.readline().strip()
    vowels = set("aeiouAEIOU")
    for ch in s:
        if ch in vowels:
            print("yes")
            return
    print("no")

if __name__ == "__main__":
    solve()
