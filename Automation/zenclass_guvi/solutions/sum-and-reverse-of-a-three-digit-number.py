n = int(input())
d1 = n // 100
d2 = (n // 10) % 10
d3 = n % 10
print(d1 + d2 + d3)
print(d3 * 100 + d2 * 10 + d1)
