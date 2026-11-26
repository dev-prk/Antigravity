import sys

def evaluate_prefix(expr):
    stack = []
    ops = {'+', '-', '*', '/'}
    for char in reversed(expr):
        if char in ops:
            if len(stack) < 2:
                return -1
            a = stack.pop()
            b = stack.pop()
            if char == '+':
                res = a + b
            elif char == '-':
                res = a - b
            elif char == '*':
                res = a * b
            elif char == '/':
                if b == 0:
                    return -1
                res = a // b
            stack.append(res)
        else:
            stack.append(int(char))
    if len(stack) != 1:
        return -1
    return stack[0]

def main():
    s = sys.stdin.readline().strip()
    if not s:
        print(-1)
        return
    tokens = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c in '+-*/':
            tokens.append(c)
            i += 1
        else:
            j = i
            while j < n and s[j].isdigit():
                j += 1
            if j > i:
                tokens.append(s[i:j])
                i = j
            else:
                i += 1
    expr = ''.join(tokens)
    result = evaluate_prefix(expr)
    print(result)

if __name__ == "__main__":
    main()
