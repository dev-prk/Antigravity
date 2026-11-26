import sys

def main():
    lines = sys.stdin.read().splitlines()
    if len(lines) < 2:
        print(-1)
        return
    
    s1 = lines[0]
    s2 = lines[1]
    
    if not s2:
        print(0)
        return
    
    n, m = len(s1), len(s2)
    
    if m > n:
        print(-1)
        return
    
    # Build LPS array for KMP
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        if s2[i] == s2[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    
    # Search using KMP
    i = j = 0
    while i < n:
        if s1[i] == s2[j]:
            i += 1
            j += 1
            if j == m:
                print(i - j)
                return
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    
    print(-1)

if __name__ == "__main__":
    main()
