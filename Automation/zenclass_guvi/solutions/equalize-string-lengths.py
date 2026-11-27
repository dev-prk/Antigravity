import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print(-1)
        return
    parts = line.split()
    if len(parts) < 2:
        print(-1)
        return
    
    s1, s2 = parts[0], parts[1]
    len1, len2 = len(s1), len(s2)
    
    if len1 == len2:
        print(s1 + s2)
    elif len1 > len2:
        print(s1[:len2] + s2)
    else:
        print(s1 + s2[:len1])

if __name__ == "__main__":
    main()
