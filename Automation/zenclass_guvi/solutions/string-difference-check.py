import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    parts = line.split()
    s1 = parts[0]
    s2 = parts[1]
    k = int(parts[2])
    
    len_diff = abs(len(s1) - len(s2))
    min_len = min(len(s1), len(s2))
    
    count = 0
    for i in range(min_len):
        if s1[i] != s2[i]:
            count += 1
    
    count += len_diff  # Account for the extra characters in the longer string
    
    if count == k:
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
