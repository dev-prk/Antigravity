import sys

def main():
    lines = sys.stdin.read().splitlines()
    s1 = lines[0] if len(lines) > 0 else ""
    s2 = lines[1] if len(lines) > 1 else ""
    
    len1 = 0
    for _ in s1:
        len1 += 1
    
    len2 = 0
    for _ in s2:
        len2 += 1
    
    # Compare lengths
    if len1 > len2:
        print(s1)
    elif len2 > len1:
        print(s2)
    else:
        # Same length, compare lexicographically
        i = 0
        while i < len1:
            if s1[i] != s2[i]:
                if s1[i] > s2[i]:
                    print(s1)
                else:
                    print(s2)
                return
            i += 1
        # Strings are equal
        print("Equal")

if __name__ == "__main__":
    main()
