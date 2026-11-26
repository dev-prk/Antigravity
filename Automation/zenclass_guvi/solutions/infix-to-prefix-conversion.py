import sys

def infix_to_prefix(expression):
    prec = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    ops = set(['+', '-', '*', '/', '^', '(', ')'])
    
    # Reverse the expression and swap '(' with ')'
    reversed_expr = expression[::-1]
    modified = []
    for char in reversed_expr:
        if char == '(':
            modified.append(')')
        elif char == ')':
            modified.append('(')
        else:
            modified.append(char)
    modified = ''.join(modified)
    
    # Stack for operators
    stack = []
    result = []
    
    for char in modified:
        if char in ops:
            if char == '(':
                stack.append(char)
            elif char == ')':
                while stack and stack[-1] != '(':
                    result.append(stack.pop())
                if stack:
                    stack.pop()  # Remove '(' from stack
            else:  # It's an operator
                while stack and stack[-1] != '(' and prec[stack[-1]] >= prec[char]:
                    result.append(stack.pop())
                stack.append(char)
        else:  # Operand
            result.append(char)
    
    # Pop remaining operators from stack
    while stack:
        result.append(stack.pop())
    
    # Reverse the result to get prefix notation
    prefix = ''.join(result[::-1])
    return prefix

# Read input from sys.stdin and strip any trailing whitespace/newlines
expression = sys.stdin.readline().strip()
result = infix_to_prefix(expression)
print(result)
