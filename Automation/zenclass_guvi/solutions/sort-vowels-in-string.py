def sort_vowels(s):
    vowels = set('aeiouAEIOU')
    vowel_list = sorted([c for c in s if c in vowels])
    result = []
    vowel_idx = 0
    for c in s:
        if c in vowels:
            result.append(vowel_list[vowel_idx])
            vowel_idx += 1
        else:
            result.append(c)
    return ''.join(result)

s = input().strip()
print(sort_vowels(s))
