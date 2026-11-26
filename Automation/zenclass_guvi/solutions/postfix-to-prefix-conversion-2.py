import sys

def postfix_to_prefix(postfix):
    stack = []
    operators = set(['+', '-', '*', '/'])
    
    for char in postfix:
        if char not in operators:
            stack.append(char)
        else:
            operand2 = stack.pop()
            operand1 = stack.pop()
            prefix = char + operand1 + operand2
            stack.append(prefix)
    
    return stack[-1] if stack else ""

def main():
    line = sys.stdin.readline().strip()
    if line:
        result = postfix_to_prefix(line)
        print(result)

if __name__ == "__main__":
    main()
