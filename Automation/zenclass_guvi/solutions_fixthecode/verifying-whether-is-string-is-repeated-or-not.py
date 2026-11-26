from collections import Counter

n = input()
count = Counter(n)
result = [char for char in n if count[char] == 1]

if result:
    print(' '.join(result))
else:
    print(-1)
