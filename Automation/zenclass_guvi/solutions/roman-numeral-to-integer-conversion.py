import sys

def roman_to_int(s):
    if not s:
        return -1
    mapping = {'I':1, 'V':5, 'X':10, 'L':50, 'C':100, 'D':500, 'M':1000}
    for ch in s:
        if ch not in mapping:
            return -1
    total = 0
    i = 0
    n = len(s)
    while i < n:
        val = mapping[s[i]]
        if i+1 < n and mapping[s[i+1]] > val:
            total -= val
            i += 1
        else:
            total += val
            i += 1
    # Validate by converting back
    def int_to_roman(num):
        if num <= 0 or num > 3999:
            return ''
        vals = [
            (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
            (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
            (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
        ]
        res = []
        for v, sym in vals:
            while num >= v:
                res.append(sym)
                num -= v
        return ''.join(res)
    if int_to_roman(total) != s:
        return -1
    return total

def main():
    data = sys.stdin.read().splitlines()
    out_lines = []
    for line in data:
        s = line.strip()
        res = roman_to_int(s)
        out_lines.append(str(res))
    sys.stdout.write('\n'.join(out_lines))

if __name__ == "__main__":
    main()
