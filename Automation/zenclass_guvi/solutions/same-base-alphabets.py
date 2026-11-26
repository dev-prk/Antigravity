import sys

def solve():
    data = sys.stdin.read().split()
    # The input consists of two strings. If fewer than two are provided,
    # treat missing ones as empty strings.
    if len(data) >= 2:
        s1, s2 = data[0], data[1]
    elif len(data) == 1:
        s1, s2 = data[0], ""
    else:
        s1, s2 = "", ""
    
    # Two strings have the same base alphabets if their sets of characters are equal.
    set1 = set(s1)
    set2 = set(s2)
    if set1 == set2:
        print('true')
    else:
        print('false')

if __name__ == "__main__":
    solve()
