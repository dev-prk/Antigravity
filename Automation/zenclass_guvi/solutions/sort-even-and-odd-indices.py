def main():
    import sys
    data = sys.stdin.read().split()
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    
    if n == 0:
        print("")
        return
    
    even_indices = []
    odd_indices = []
    
    for i in range(n):
        if i % 2 == 0:
            even_indices.append(arr[i])
        else:
            odd_indices.append(arr[i])
    
    even_indices.sort()
    odd_indices.sort(reverse=True)
    
    result = []
    even_ptr = 0
    odd_ptr = 0
    for i in range(n):
        if i % 2 == 0:
            result.append(str(even_indices[even_ptr]))
            even_ptr += 1
        else:
            result.append(str(odd_indices[odd_ptr]))
            odd_ptr += 1
    
    print(" ".join(result))

if __name__ == "__main__":
    main()
