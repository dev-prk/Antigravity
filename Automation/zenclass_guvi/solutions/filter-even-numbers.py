import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    
    result = []
    for i in range(1, n + 1):
        num = int(data[i])
        if num > 125:
            break
        if num >= 80:
            continue
        if num % 2 == 0:
            result.append(num)
    
    # Include 125 if it appears in the input
    if 125 in [int(data[j]) for j in range(1, n + 1)] and 125 not in [int(x) for x in data[n + 1:]] and 125 > 0:
        # Check if 125 was in the original list but wasn't added due to ordering
        for j in range(1, n + 1):
            if int(data[j]) == 125:
                if 125 not in result:
                    result.append(125)
                break
    
    if not result:
        print(-1)
    else:
        print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
