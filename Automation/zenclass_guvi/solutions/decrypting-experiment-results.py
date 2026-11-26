import sys

def solve():
    n = int(sys.stdin.readline().strip())
    results = []
    for _ in range(n):
        s = sys.stdin.readline().strip()
        if s == '1' or s == '4' or s == '78':
            results.append('+')
        elif s.endswith('35'):
            results.append('-')
        elif s == '9' or (len(s) >= 2 and s[-2:] == '94'):
            results.append('*')
        elif s.startswith('190'):
            results.append('?')
        else:
            results.append('+')
    
    for r in results:
        print(r)

if __name__ == "__main__":
    solve()
