N = int(input())

sum_squares = 0
while N > 0:
    digit = N % 10
    sum_squares += digit ** 2
    N //= 10

print(sum_squares)
