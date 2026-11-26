import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    elements = list(map(int, data[1:1+n]))
    
    first_zero_idx = -1
    second_zero_idx = -1
    
    for i in range(len(elements)):
        if elements[i] == 0:
            if first_zero_idx == -1:
                first_zero_idx = i
            elif second_zero_idx == -1:
                second_zero_idx = i
                break
    
    if first_zero_idx == -1 or second_zero_idx == -1:
        print(-1)
    else:
        result = elements[first_zero_idx + 1:second_zero_idx]
        if not result:
            print(-1)
        else:
            print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
