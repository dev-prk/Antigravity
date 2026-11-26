import sys, math

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print(1)
        return
    nums = list(map(int, data[1:1+n]))
    ans = 1
    for a in nums:
        if a == 0:
            ans = 0
            break
        ans = ans // math.gcd(ans, a) * a
    print(ans)

if __name__ == "__main__":
    main()
