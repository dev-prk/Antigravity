import sys

def decrypt(s):
    result = []
    i = 0
    n = len(s)
    
    while i < n:
        if s[i].isdigit():
            num = 0
            while i < n and s[i].isdigit():
                num = num * 10 + int(s[i])
                i += 1
            if i < n and s[i] == '[':
                i += 1
                start = i
                bracket_count = 1
                while i < n and bracket_count > 0:
                    if s[i] == '[':
                        bracket_count += 1
                    elif s[i] == ']':
                        bracket_count -= 1
                    i += 1
                inner = decrypt(s[start:i-1])
                result.append(inner * num)
        elif s[i].isalpha():
            result.append(s[i])
            i += 1
        else:
            i += 1
    
    return ''.join(result)

def main():
    s = sys.stdin.readline().strip()
    if '[' not in s and ']' not in s:
        print(s)
    else:
        print(decrypt(s))

if __name__ == "__main__":
    main()
