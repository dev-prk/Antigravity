n = int(input().strip())
if n == 0:
    print("NULL")
else:
    result = [str(9 * i) for i in range(1, n + 1)]
    print(" ".join(result))
