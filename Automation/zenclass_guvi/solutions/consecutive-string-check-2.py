import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        print('no')
        return
    
    first_line = data[0].split()
    if len(first_line) < 2:
        print('no')
        return
    
    try:
        N = int(first_line[0])
        K = int(first_line[1])
    except:
        print('no')
        return
    
    if N < K:
        print('no')
        return
    
    strings = []
    for i in range(1, min(N + 1, len(data))):
        strings.append(data[i].strip())
    
    if len(strings) < N:
        print('no')
        return
    
    if K == 1:
        print('yes')
        return
    
    count = 1
    for i in range(1, N):
        if strings[i] == strings[i-1]:
            count += 1
            if count >= K:
                print('yes')
                return
        else:
            count = 1
    
    print('no')

if __name__ == "__main__":
    main()
