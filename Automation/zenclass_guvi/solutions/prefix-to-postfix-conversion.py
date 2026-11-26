import sys

def prefix_to_postfix(expr: str) -> str:
    stack = []
    for ch in reversed(expr):
        if ch.isspace():
            continue
        if ch in "+-*/^":  # treat common operators as operator
            if len(stack) < 2:
                # invalid expression, but just return
                return ""
            op1 = stack.pop()
            op2 = stack.pop()
            stack.append(op1 + op2 + ch)
        else:
            stack.append(ch)
    return stack[0] if stack else ""

def main():
    data = sys.stdin.read()
    expr = ''.join(data.split())  # remove all whitespace
    result = prefix_to_postfix(expr)
    sys.stdout.write(result)

if __name__ == "__main__":
    main()
