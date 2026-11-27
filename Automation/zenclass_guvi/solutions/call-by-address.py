# Read two integers from input
a, b = map(int, input().split())

# Print values before function call
print(f"Before function call: {a} {b}")

# Swap using call by address simulation
def swap(x, y):
    return y, x

# Call function to swap
result = swap(a, b)
a, b = result

# Print values inside function after swapping
print(f"Inside function: {a} {b}")

# Print values after function call
print(f"After function call: {a} {b}")
