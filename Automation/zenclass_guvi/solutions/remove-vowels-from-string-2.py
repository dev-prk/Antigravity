def remove_vowels(s):
    vowels = 'aeiouAEIOU'
    return ''.join([char for char in s if char not in vowels])

s = input().strip()
result = remove_vowels(s)
print(result)
