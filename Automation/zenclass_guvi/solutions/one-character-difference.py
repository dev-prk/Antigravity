import sys

def is_one_difference(s1, s2):
    if len(s1) != len(s2):
        return 'no'
    diff_count = 0
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            diff_count += 1
            if diff_count > 1:
                return 'no'
    return 'yes' if diff_count == 1 else 'no'

def main():
    line = sys.stdin.readline().strip()
    if ' ' in line:
        parts = line.split()
        if len(parts) >= 2:
            s1 = parts[0].strip()
            s2 = parts[1].strip()
            print(is_one_difference(s1, s2))
            return
    
    s1 = sys.stdin.readline().strip()
    s2 = sys.stdin.readline().strip()
    print(is_one_difference(s1, s2))

if __name__ == "__main__":
    main()
