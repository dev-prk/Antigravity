s = input().strip()
reversed_s = s[::-1]
result = reversed_s[0].upper() + reversed_s[1:] if reversed_s else ""
print(result)
