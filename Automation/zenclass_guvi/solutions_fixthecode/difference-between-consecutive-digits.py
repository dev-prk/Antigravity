n = int(input())
a = []
for j in range(1, n + 1):
    i = j
    digits = []
    while i != 0:
        digits.append(i % 10)
        i //= 10
    digits = digits[::-1]
    if len(digits) == 1:
        continue
    valid = True
    for k in range(len(digits) - 1):
        if abs(digits[k] - digits[k + 1]) != 1:
            valid = False
            break
    if valid:
        a.append(j)
if len(a) == 0:
    print('-1')
else:
    print(' '.join(map(str, a)))
