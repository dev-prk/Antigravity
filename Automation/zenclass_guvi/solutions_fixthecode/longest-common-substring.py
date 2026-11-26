def longest_common_substring_three():
    a, b, c = input().split()
    m, n, p = len(a), len(b), len(c)
    
    max_len = 0
    result = ""
    
    for i in range(m):
        for j in range(n):
            for k in range(p):
                length = 0
                while i + length < m and j + length < n and k + length < p:
                    if a[i + length] == b[j + length] == c[k + length]:
                        length += 1
                    else:
                        break
                if length > max_len:
                    max_len = length
                    result = a[i:i + length]
    
    if max_len == 0:
        print(-1)
    else:
        print(result)

longest_common_substring_three()
