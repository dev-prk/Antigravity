n = int(input())
b = [int(x) for x in input().split()]
c = [int(x) for x in input().split()]
c.reverse()
if b == c:
    print("yes", end="")
else:
    print("no", end="")
