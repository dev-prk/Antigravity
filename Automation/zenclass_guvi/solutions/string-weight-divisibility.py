s = input()
vowels = 'aeiou'
weight = 0
for ch in s:
    if ch in vowels:
        weight += ord(ch)
print(1 if weight % 8 == 0 else 0)
