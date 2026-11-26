a = int(input())
for i in range(1, a + 1):
    b_count = a - i
    stars = 2 * i - 1
    line = 'b' * b_count + '*' * stars + 'b' * b_count
    print(line)
