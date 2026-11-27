import sys

def main():
    data = sys.stdin.read().splitlines()
    idx = 0
    n = int(data[idx])
    idx += 1
    dictionary = set()
    for _ in range(n):
        word = data[idx].strip()
        idx += 1
        dictionary.add(word)
    
    q = int(data[idx])
    idx += 1
    results = []
    for _ in range(q):
        s = data[idx].strip()
        idx += 1
        found = False
        for i in range(1, len(s)):
            s1 = s[:i]
            s2 = s[i:]
            if s1 in dictionary and s2 in dictionary:
                found = True
                break
        results.append("YES" if found else "NO")
    
    sys.stdout.write("\n".join(results) + "\n")

if __name__ == "__main__":
    main()
