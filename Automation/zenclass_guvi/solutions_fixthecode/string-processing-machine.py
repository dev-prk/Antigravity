n = int(input())
strings = [input() for _ in range(n)]

for i in range(1, n):
    for j in range(i):
        if strings[j].startswith(strings[i]):
            print("Bad input", strings[i])
            exit()

print("1000 Gold coins dispensed")
