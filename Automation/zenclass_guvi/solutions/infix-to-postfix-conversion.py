import sys


def main():
    data = sys.stdin.read()
    # Remove all whitespace (handles trailing spaces, newlines, N=0)
    expr = ''.join(data.split())

    prec = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    right_assoc = {'^'}

    output = []
    stack = []

    for c in expr:
        if c.isalnum():
            output.append(c)
        elif c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack:
                stack.pop()  # discard '('
        elif c in prec:
            while stack and stack[-1] in prec:
                top = stack[-1]
                if (c in right_assoc and prec[top] < prec[c]) or \
                   (c not in right_assoc and prec[top] >= prec[c]):
                    output.append(stack.pop())
                else:
                    break
            stack.append(c)

    while stack:
        output.append(stack.pop())

    sys.stdout.write(''.join(output))


main()
