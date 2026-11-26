import sys

def main():
    data = sys.stdin.read().splitlines()
    # Filter out empty lines, but we need two lines of input
    # The input consists of two lines: S1 and S2
    lines = [line.strip() for line in data if line.strip() != '']
    if len(lines) < 2:
        # Not enough input, print 'no'
        print('no')
        return
    
    s1 = lines[0]
    s2 = lines[1]
    
    combined = s1 + s2
    # Check if all 26 uppercase letters appear exactly once
    if len(combined) != 26:
        print('no')
    else:
        # Check if all characters are uppercase letters
        # and no duplicates
        seen = set()
        valid = True
        for ch in combined:
            if not ('A' <= ch <= 'Z'):
                valid = False
                break
            if ch in seen:
                valid = False
                break
            seen.add(ch)
        if valid and len(seen) == 26:
            print('yes')
        else:
            print('no')

if __name__ == '__main__':
    main()
