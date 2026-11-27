print("Before function call:", end=" ")
a, b = map(int, input().split())
print(a, b)
print("Inside function:", end=" ")

def swap(x, y):
    temp = x
    x = y
    y = temp
    return x, y

swapped_a, swapped_b = swap(a, b)
print(swapped_a, swapped_b)
print("After function call:", end=" ")
print(a, b)
