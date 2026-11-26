mylist = input().split()
mydict = {}
for name in mylist:
    if name not in mydict:
        mydict[name] = 1
    else:
        mydict[name] = mydict[name] + 1

max_votes = max(mydict.values())
candidates = []
for name in mydict:
    if mydict[name] == max_votes:
        candidates.append(name)

candidates.sort()
winner = candidates[0]
print(winner, max_votes)
