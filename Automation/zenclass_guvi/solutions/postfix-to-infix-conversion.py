import sys

def postfix_to_infix(expr: str) -> str:
    if not expr:
        return ""
    ops = set('+-*/^%')
    stack = []
    for ch in expr:
        if ch.isspace():
            continue
        if ch in ops:
            if len(stack) < 2:
                return "-1"
            right = stack.pop()
            left = stack.pop()
            stack.append(f"{left}{ch}{right}")
        else:
            stack.append(ch)
    return stack[0] if len(stack) == 1 else "-1"

def main():
    data = sys.stdin.read()
    expr = data.strip()
    result = postfix_to_infix(expr)
    print(result)

if __name__ == "__main__":
    main()
