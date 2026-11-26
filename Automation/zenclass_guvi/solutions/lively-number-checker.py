from collections import Counter

n = input().strip()
freq = Counter(n)
freq_values = list(freq.values())

if all(v == freq_values[0] for v in freq_values):
    print(1)
else:
    print(0)
