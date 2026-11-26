import sys
from collections import defaultdict

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        print("No maximal palindrome")
        return
    
    first_line = data[0].strip()
    if not first_line:
        print("No maximal palindrome")
        return

    parts = first_line.split()
    if len(parts) < 2:
        print("No maximal palindrome")
        return

    try:
        N = int(parts[0])
        M = int(parts[1])
    except:
        print("No maximal palindrome")
        return

    if N <= 0 or M <= 0:
        print("No maximal palindrome")
        return

    list1 = []
    list2 = []
    idx = 1
    
    for i in range(N):
        if idx < len(data):
            list1.append(data[idx].strip())
            idx += 1
        else:
            list1.append("")
    
    for i in range(M):
        if idx < len(data):
            list2.append(data[idx].strip())
            idx += 1
        else:
            list2.append("")

    # Build trie for reversed prefixes of list2
    # key: (reverse(prefix)) -> list of original prefixes
    trie = defaultdict(list)
    
    for s in list2:
        for i in range(1, len(s) + 1):
            prefix = s[:i]
            rev_prefix = prefix[::-1]
            trie[rev_prefix].append(prefix)

    best_len = -1
    best_pal = ""
    
    for s in list1:
        for i in range(len(s)):
            suffix = s[i:]
            if suffix in trie:
                for prefix in trie[suffix]:
                    pal = suffix + prefix
                    pal_len = len(pal)
                    if pal_len > best_len or (pal_len == best_len and pal < best_pal):
                        best_len = pal_len
                        best_pal = pal

    if best_len <= 0:
        print("No maximal palindrome")
    else:
        print(best_pal)

if __name__ == "__main__":
    main()
