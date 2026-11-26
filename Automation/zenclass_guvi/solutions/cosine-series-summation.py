import math

data = input().split()
degree = int(data[0])
terms = int(data[1])

rad = math.radians(degree)
total = 0.0

for i in range(terms):
    numerator = (-1) ** i * (rad ** (2 * i))
    denominator = 1
    for j in range(1, 2 * i + 1):
        denominator *= j
    total += numerator / denominator

print(round(total, 2))
