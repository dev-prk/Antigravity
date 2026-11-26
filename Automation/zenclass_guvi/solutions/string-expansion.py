import sys

def expand_string(s):
    result = []
    i = 0
    n = len(s)
    
    while i < n:
        if s[i].isdigit():
            num = 0
            while i < n and s[i].isdigit():
                num = num * 10 + int(s[i])
                i += 1
            
            if i < n and s[i] == '(':
                i += 1
                start = i
                balance = 1
                while i < n and balance != 0:
                    if s[i] == '(':
                        balance += 1
                    elif s[i] == ')':
                        balance -= 1
                    i += 1
                inner = s[start:i-1]
                expanded_inner = expand_string(inner)
                result.append(expanded_inner * num)
        elif s[i] == ')':
            i += 1
        else:
            result.append(s[i])
            i += 1
    
    return ''.join(result)

s = sys.stdin.readline().strip()
print(expand_string(s))
