import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    L = int(data[0])
    R = int(data[1])
    # Ensure bounds
    if L > R:
        print(0)
        return
    limit = 100000
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for p in range(2, int(limit ** 0.5) + 1):
        if is_prime[p]:
            for multiple in range(p * p, limit + 1, p):
                is_prime[multiple] = False
    count = 0
    for i in range(L, R + 1):
        if i >= 2 and is_prime[i]:
            count += 1
    print(count)

if __name__ == "__main__":
    main()
