n = abs(int(input()))
s = str(n)

if n < 0 and n != 0:
    first = int(s[0])
    last = int(s[-1])
    print("yes" if (first + last) % 4 == 0 else "no")
elif n >= 0:
    if n < 10:
        print("yes")
    else:
        last_two = [int(d) for d in s[-2:]]
        print("yes" if sum(last_two) % 4 == 0 else "no")
else:
    print("no" if n != 0 else "yes")
