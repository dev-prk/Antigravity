n = int(input())
s = list(map(int, input().split()))
g = "yes"
if n < 3:
    print(g)
else:
    for i in range(1, n-1):
        if i % 2 == 1:
            if not (s[i] > s[i-1] and s[i] > s[i+1]):
                g = "no"
                break
        else:
            if not (s[i] < s[i-1] and s[i] < s[i+1]):
                g = "no"
                break
print(g)
