import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    m = int(data[0])
    n = int(data[1])
    
    list1 = list(map(int, data[2:2+m]))
    list2 = list(map(int, data[2+m:2+m+n]))
    
    i, j = 0, 0
    result = []
    
    while i < m and j < n:
        if list1[i] <= list2[j]:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1
    
    while i < m:
        result.append(list1[i])
        i += 1
    
    while j < n:
        result.append(list2[j])
        j += 1
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
