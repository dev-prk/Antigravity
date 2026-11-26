import sys

def main():
    s = sys.stdin.readline().rstrip('\n')
    ans = 0
    i = 0
    n = len(s)
    while i < n:
        j = i
        while j < n and s[j] == s[i]:
            j += 1
        L = j - i
        if L >= 3:
            ans += (L - 1) // 2
        i = j
    print(ans)

if __name__ == "__main__":
    main()
