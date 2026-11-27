import sys

def generate_combinations(s):
    n = len(s)
    if n == 0:
        print(-1)
        return
    results = [s]
    for i in range(n - 1, 0, -1):
        new_results = []
        for r in results:
            new_results.append(r[:i] + ' ' + r[i:])
        results.extend(new_results)
    for r in results:
        print(r)

def main():
    s = sys.stdin.readline().strip()
    generate_combinations(s)

if __name__ == "__main__":
    main()
