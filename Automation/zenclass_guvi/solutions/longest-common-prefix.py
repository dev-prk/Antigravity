import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        print("")
        return
    
    n = int(data[0].strip())
    if n == 0:
        print("")
        return
    
    strings = []
    for i in range(1, n + 1):
        if i < len(data):
            strings.append(data[i].strip())
        else:
            strings.append("")
    
    if n == 1:
        print(strings[0])
        return
    
    first = strings[0]
    min_len = len(first)
    for s in strings[1:]:
        min_len = min(min_len, len(s))
    
    lcp = []
    for j in range(min_len):
        char = first[j]
        for s in strings[1:]:
            if s[j] != char:
                print(''.join(lcp))
                return
        lcp.append(char)
    
    print(''.join(lcp))

if __name__ == "__main__":
    main()
