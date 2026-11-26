import sys

def main():
    s = sys.stdin.readline().strip()
    
    max_consecutive = 0
    current_consecutive = 0
    has_one = False
    
    for char in s:
        if char == '1':
            current_consecutive += 1
            has_one = True
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 0
    
    if has_one:
        print(max_consecutive)
    else:
        print(-1)

if __name__ == "__main__":
    main()
