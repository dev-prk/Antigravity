from itertools import permutations
s = input()
L = [''.join(x) for x in permutations(s)]
L2 = list(set(L))
sum1 = 0
for x in L2:
    sum1 += int(x)
print(sum1)
